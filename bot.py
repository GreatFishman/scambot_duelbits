import time
import asyncio
import sys, os
import multiprocessing as mp
from pyppeteer import launch
from telegram.ext import Updater, CallbackContext
from telegram import Update
from telegram.ext import CommandHandler

updater = Updater(token='5259698150:AAHN7GRM_Sv9S8ocWh--gUZqd5QRNCBKATk', use_context = True)

MAIN = 'https://duelbits.com/?modal=Cashier&tab=withdraw&method=csgo'

async def crawlerFunction():
    try:
        os.system("taskkill /f /im chrome.exe")
        browser = await launch(headless=True, 
                                executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 
                                userDataDir="C:\\Users\\Rene-Desktop\\AppData\\Local\\Google\\Chrome\\User",
                                args=['--no-sandbox'])
        page = await browser.newPage()
        await page.goto(MAIN)
        print("crawler started. gathering data")
        await asyncio.sleep(3)
        firstCrawl = True
        priceFloor = 100
        items = []
        while(1):
            if(firstCrawl): #get every entry without a percentage element and put it into a list, then load more entries and repeat until priceFloor
                currentPrice = 10000
                while(currentPrice > priceFloor):
                    #print("trace")
                    items = await page.evaluate('''() => {
                        function Sleep(milliseconds) {
                        return new Promise(resolve => setTimeout(resolve, milliseconds));
                        }
                        var noPercentageItems = []
                        var name = ''
                        var price = ''
                        let items = document.getElementsByClassName('styles__Item-sc-dvvtb4-1 bMvsrN');
                        Array.from(items).forEach((item) => {
                            let children = item.getElementsByClassName('styles__Bottom-sc-dvvtb4-8 jwlkUa')[0].getElementsByTagName('div').length
                            price = item.getElementsByClassName('styles__Price-sc-dvvtb4-9 hZKTNM info-widget')[0].textContent
                            name = item.getElementsByClassName('styles__Name-sc-dvvtb4-6 eZrmyQ')[0].textContent
                            var onlineStatus = item.getElementsByClassName('styles__OnlineIndicator-sc-dvvtb4-4 huUufB')[0]
                            if(children == 1 && (typeof onlineStatus !== 'undefined')) { //only has price, no percentage
                                name = item.getElementsByClassName('styles__Name-sc-dvvtb4-6 eZrmyQ')[0].textContent
                                noPercentageItems.push([name,price])
                            }
                        })
                        noPercentageItems.push([name,price])
                        return noPercentageItems

                    }''')
                    currentPrice = float(items[-1][1].replace(',','')) #last entries' price, remove commas then parse string
                    print('Current lowest price:' + str(currentPrice))
                    items.pop()
                    ##click the load more button, style is unique
                    await page.waitForSelector('button[style="width: fit-content; height: 52px; padding: 0px 34px;"]', timeout=60000)
                    await page.click('button[style="width: fit-content; height: 52px; padding: 0px 34px;"]')
                    await asyncio.sleep(2)
                ##end while
                #firstCrawl = False

            # else: #same as above, but no need for a loop to open the items
            #     print("loop")
            #     #await page.waitForSelector('button[class="styles__Button-sc-1v554gb-0 bRLLyP styles__NewListingButton-sc-falim1 gaibCI"]')
            #     print("loading new listings")
            #     await page.click('button[class="styles__Button-sc-1v554gb-0 bRLLyP styles__NewListingButton-sc-falim1 gaibCI"]')
            #     print("loading new listings2")
            #     items = await page.evaluate('''() => {
            #             function Sleep(milliseconds) {
            #                return new Promise(resolve => setTimeout(resolve, milliseconds));
            #             }
            #             var noPercentageItems = []
            #             var name = ''
            #             var price = ''
            #             let items = document.getElementsByClassName('styles__Item-sc-dvvtb4-1 bMvsrN');
            #             Array.from(items).forEach((item) => {
            #                 let children = item.getElementsByClassName('styles__Bottom-sc-dvvtb4-8 jwlkUa')[0].getElementsByTagName('div').length
            #                 price = item.getElementsByClassName('styles__Price-sc-dvvtb4-9 hZKTNM info-widget')[0].textContent
            #                 name = item.getElementsByClassName('styles__Name-sc-dvvtb4-6 eZrmyQ')[0].textContent
            #                 var onlineStatus = item.getElementsByClassName('styles__OnlineIndicator-sc-dvvtb4-4 huUufB')[0]
            #                 if(children == 1 && (typeof onlineStatus !== 'undefined')) { //only has price, no percentage
            #                     name = item.getElementsByClassName('styles__Name-sc-dvvtb4-6 eZrmyQ')[0].textContent
            #                     noPercentageItems.push([name,price])
            #                 }
            #             })
            #             return noPercentageItems

            #         }''')
            print(items) ## Nico: 2120144191 Ich: 568701131
            if(len(items) > 1):
                updater.bot.send_message(chat_id='2120144191', text=str(len(items)) + " Idioten verkaufen ihre Skins für 0%!!")
            elif(len(items) == 1):
                updater.bot.send_message(chat_id='2120144191', text="Ein mieser Gumbo verkauft seinen Skin für 0%!!")

            for item in items:
                updater.bot.send_message(chat_id='2120144191',text=(str(item[0]) + " für " + str(item[1])))

            await asyncio.sleep(60)
            await page.reload()
    except Exception as e:
        print(sys.exc_info()[0])
        raise



def crawlerThread():
    print("starting crawler...")
    asyncio.run(crawlerFunction())

def telegramThread():
    print("starting telegram bot...")
    updater.dispatcher.add_handler(CommandHandler('start',start))
    updater.start_polling()
    print("telegram bot started!")
    updater.idle()

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    res1 = pool.apply_async(telegramThread)
    res2 = pool.apply_async(crawlerThread)
    pool.close()
    pool.join()
    