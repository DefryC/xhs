import datetime
import json
from time import sleep
from xhs import XhsClient, DataFetchError, help
from playwright.sync_api import sync_playwright


def sign(uri, data=None, a1="18b838aed62qz1gg0j8pzo0vj9b8onj4g3jux0gfc50000326500", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = "stealth.min.js"
                chromium = playwright.chromium

                # 如果一直失败可尝试设置成 False 让其打开浏览器，适当添加 sleep 可查看浏览器状态
                browser = chromium.launch(headless=True)

                browser_context = browser.new_context()
                browser_context.add_init_script(path=stealth_js_path)
                context_page = browser_context.new_page()
                context_page.goto("https://www.xiaohongshu.com")
                browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                context_page.reload()
                # 这个地方设置完浏览器 cookie 之后，如果这儿不 sleep 一下签名获取就失败了，如果经常失败请设置长一点试试
                sleep(1)
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception:
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")


if __name__ == '__main__':
    cookie = "abRequestId=70fe05b7-70b2-56db-a0f1-f2fa8beb2df5; webBuild=3.13.6; xsecappid=xhs-pc-web; a1=18b838aed62qz1gg0j8pzo0vj9b8onj4g3jux0gfc50000326500; webId=c35bdbe2d22b0cb90392c668e5c6dfde; gid=yYDYqY0iJDkWyYDYqY0dfq8kKJAuykk8VYUuViSl8hVjD728YlIV4C888qJK2888K4fKjqY2; web_session=040069b10e0d7756e6ac522d75374ba1bc63e1; unread={%22ub%22:%226537b527000000001e02220f%22%2C%22ue%22:%22653ba5070000000025008fa3%22%2C%22uc%22:27}; websectiga=2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d; acw_tc=f807dbafb742eee8331e8866e25f841cfcf167baa6ac774b76ee7c873f2f998a; sec_poison_id=d83a2b72-25cd-4157-bffa-83f840e2fc91"

    xhs_client = XhsClient(cookie, sign=sign)
    print(datetime.datetime.now())

    for _ in range(10):
        # 即便上面做了重试，还是有可能会遇到签名失败的情况，重试即可
        try:
            note = xhs_client.get_note_by_id("6505318c000000001f03c5a6")
            print(json.dumps(note, indent=4))
            print(help.get_imgs_url_from_note(note))
            break
        except DataFetchError as e:
            print(e)
            print("失败重试一下下")
