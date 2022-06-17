import requests
import aiohttp
import asyncio
import json
from aiohttp import ClientSession
import time

start_time = time.time()

API_BASE_URL = "https://kong-tatasky.videoready.tv/"

clist = []


def extract_fields_from_response(response, channel):
    data_meta = response.get('data')['meta']
    channel_meta = response.get('data')['channelMeta']
    channel_detail_dict = response.get('data')['detail']
    channel_genre = response.get('data')['channelMeta']['genre']
    channel_lang = channel.get('subTitles')
    channelgenre = channel_lang + channel_genre
    
    if data_meta:
        onechannel = {
            "channel_id": str(channel.get('id')),
            "channel_name": channel_meta.get('name'),
            "channel_license_url": channel_detail_dict.get('dashWidewineLicenseUrl'),
            "channel_url": channel_detail_dict.get('dashWidewinePlayUrl'),
            "channel_entitlements": channel_detail_dict.get('entitlements'),
            "channel_logo": channel_meta.get('logo'),
            "channel_genre": ";".join(f"{genre}" for genre in channelgenre)
        }
        return (onechannel)
    else:
        print("Exception on Channel " + str(channel.get("id")))
        

async def getchannelinfo(channel, session):
    channelId = str(channel.get('id'))
    url = "{}content-detail/pub/api/v2/channels/{}".format(API_BASE_URL, channelId)
    try:
        response = await session.request(method='GET', url=url)
        #response.raise_for_status()
        #print(f"Response status ({url}): {response.status}")
    
    except Exception as err:
        print(f"An error ocurred: {err}")
    response_json = await response.json()
    return response_json


async def getChunks(channel, session):
    try:
        response = await getchannelinfo(channel, session)
        parsed_response = extract_fields_from_response(response, channel)
        return parsed_response
    except Exception as err:
        print(f"Exception occured: {err}")


def saveChannelsToFile():
    with open("allCh.json", "w") as channel_list_file:
        json.dump(clist, channel_list_file)
        print("Saving " + str(len(clist)) + " to file " + channel_list_file.name)
        channel_list_file.close()


async def getchannels():
    #channel_list = []
    #num = input("Enter total channel number: ")
    url = API_BASE_URL + "content-detail/pub/api/v1/channels?limit=586" #+ num
    resp = requests.get(url)
    channellist = resp.json()['data']['list']
    #for item in channellist:
        #chnlid = str(item["id"])
        #chnlid = item["id"]
        #channel_list.append(chnlid)
    print("Total channels... " + str(len(channellist)))
    
    async with ClientSession() as session:
        data = await asyncio.gather(*[getChunks(channel, session) for channel in channellist])
        for item in data:
            if item is not None:
                clist.append(item)
    #print("Saving " + str(len(clist)) + " to file...")
    saveChannelsToFile()
    
    
if __name__=='__main__':
    #asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(getchannels())
    print("Completed in - %s seconds" % (time.time() - start_time))
