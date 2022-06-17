import jwtoken
import asyncio
import aiohttp
from aiohttp import ClientSession
#import time

#start_time = time.time()


def m3u_from_response(response, channel):
    m3ustr = ''
    kodiPropLicenseType = "#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha"
    kodiPropLicenseUrl = ''
    
    ls_session_key = response.get('data')['token']
    
    for item in response:
        if ls_session_key != "":
            licenseUrl = channel['channel_license_url'] + "&ls_session=" + ls_session_key
            kodiPropLicenseUrl = "#KODIPROP:inputstream.adaptive.license_key=" + licenseUrl
        else:
            print("Didn't get license for channel: Id: {0} Name:{1}".format(channel['channel_id'],
                                                                            channel['channel_name']))
            print('Continuing...Please get license manually for channel :', channel['channel_name'])
        #m3ustr += "#EXTINF:-1  " + "tvg-id=ts" + channel['channel_id'] + "  tvg-logo=" + channel['channel_logo'] + "   group-title=" + channel['channel_genre'][0] + ",   "
        m3ustr += "#EXTINF:-1  " + "tvg-id=ts" + channel['channel_id'] + "  tvg-logo=" + channel['channel_logo'] + "   group-title=" + '"' + channel['channel_genre'] + '"' + ",   "
        m3ustr += channel['channel_name'] + "\n" + kodiPropLicenseType + "\n" + kodiPropLicenseUrl + "\n" + channel['channel_url'] + "\n\n"
        #print(channel['channel_id'])
        return m3ustr


async def processTokenChunks(sem, channel, session):
    try:
        response = await jwtoken.generateJWT(sem, channel['channel_id'], session)
        parsed_response = m3u_from_response(response, channel)
        return parsed_response
    except Exception as err:
        print(f"Exception occured: {err}")


async def m3ugen():
    tc = '#EXTM3U    x-tvg-url="http://www.tsepg.cf/epg.xml.gz" \n\n'
    
    channelList = jwtoken.getUserChannelSubscribedList()
    #print("Found total {0} channels subscribed by user".format(len(channelList)))
    
    sem = asyncio.Semaphore(100)
    
    async with ClientSession() as session:
        data = await asyncio.gather(*[processTokenChunks(sem, channel, session) for channel in channelList])
        for item in data:
            tc += item
            
    print("================================================================")
    print("Found total {0} channels subscribed by user \nSaving them to m3u file".format(len(channelList)))
    print("================================================================")

    saveM3ustringtofile(tc)


def saveM3ustringtofile(tc):
    with open("allChannelPlaylist.m3u", "w") as allChannelPlaylistFile:
        allChannelPlaylistFile.write(tc)
        #print("Saved to file " + allChannelPlaylistFile.name)


def getPrintNote():
    s = " *****************************************************\n" + "Welcome To TataSky Channel Generation Script\n" + \
        "**********************************************************\n" + \
        "- Using this script you can generate playable links based on the channels you have subscribed to \n" + \
        "- You can always read the README.md file if you don't know how to use the generated file \n" + \
        "- You can login using your password or generate an OTP. You need to enter both the Registered Mobile Number \n" + \
        "\n Caution: This doesn't promote any kind of hacking or compromising anyone's details"

    return s


if __name__ == '__main__':
    #asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(m3ugen())
    #print("Completed in - %s seconds" % (time.time() - start_time))
