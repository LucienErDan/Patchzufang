import requests
# 用于解析html数据的框架
from bs4 import BeautifulSoup
# 用于操作excel的框架
from xlwt import *
import json
import re
import  time

# 创建一个工作
book = Workbook(encoding='utf-8');
# 向表格中增加一个sheet表，sheet1为表格名称 允许单元格覆盖
sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)

# 设置样式
style = XFStyle();
pattern = Pattern();
pattern.pattern = Pattern.SOLID_PATTERN;
pattern.pattern_fore_colour="0x00";
style.pattern = pattern;
# 设置列标题
sheet.write(0, 0, "标题")
sheet.write(0, 1, "地区")
sheet.write(0, 2, "区方向")
sheet.write(0, 3, "小区名")
sheet.write(0, 4, "平米")
sheet.write(0, 5, "卧室方向")
sheet.write(0, 6, "几厅几卧")
sheet.write(0, 7, "元/月")

# 设置列宽度
sheet.col(0).width = 0x0d00 + 200*50
sheet.col(1).width = 0x0d00 + 20*50
sheet.col(2).width = 0x0d00 + 10*50
sheet.col(3).width = 0x0d00 + 120*50
sheet.col(4).width = 0x0d00 + 1*50
sheet.col(5).width = 0x0d00 + 50*50

# 指定爬虫所需的上海各个区域名称
citys = ['xinchengqu', 'beilin', 'yanta','baqiao']

def getHtml(city):
    try:
        url = 'https://xa.lianjia.com/zufang/'+city
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        request = requests.get(url=url, headers=headers)
        # 获取源码内容比request.text好，对编码方式优化好
        respons = request.content
        # 使用bs4模块，对响应的链接源代码进行html解析，后面是python内嵌的解释器，也可以安装使用lxml解析器
        soup = BeautifulSoup(respons, 'html.parser')
        # 获取类名为c-pagination的div标签，是一个列表
        pageDiv = soup.select('div .content__pg')[0]
        totalPage =dict(pageDiv.attrs)['data-totalpage'];
        #totalPage = '1';
        curPage =dict(pageDiv.attrs)['data-curpage'];
        # 如果标签a标签数大于1，说明多页，取出最后的一个页码，也就是总页数
        for i in range(int(totalPage)):
            pageIndex=i+1;
            print(city+"=========================================第 " + str(pageIndex) + " 页")
            saveData(city, url, str(pageIndex));
            time.sleep(5)
    except Exception as e:
        print(e);

def getreRes(reExpre,src):
    m = re.search(reExpre,src);
    if m is not None:
        res =m.group()
    return res;
# 调用方法解析每页数据，并且保存到表格中
def saveData(city, url, pageIndex):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    urlStr =url+'/pg'+pageIndex+'/#contentList';
    print(urlStr);
    print("\n")
    html = requests.get(urlStr, headers=headers).content;
    soup = BeautifulSoup(html, 'lxml')
    liList = soup.findAll("div", {"class": "content__list--item"})
    index=0;
    for info in liList:
        title =info.find("p",class_="content__list--item--title twoline").find("a").text;
        address =info.find("p",class_="content__list--item--des").find("a").text;
        areaetc =info.find("p",class_="content__list--item--des").text;
        if '地下室' in areaetc:
            break;
        area =getreRes('..㎡',areaetc);

        shitingwei =getreRes('.室.厅.卫',areaetc);

        timeonline =info.find("p",class_="content__list--item--time oneline").text;
        priceall =info.find("span",class_="content__list--item-price").text;
        price = getreRes('\d+\.?\d*',priceall);
        #print(address);

        # flood = info.find("div", class_="flood").text
        # subway = info.find("div", class_="tag").findAll("span", {"class", "subway"});
        # subway_col="";
        # if len(subway) > 0:
        #     subway_col = subway[0].text;

        #taxfree = info.find("div", class_="tag").findAll("span", {"class", "taxfree"});
        taxfree_col="";
        # if len(taxfree) > 0:
        #     taxfree_col = taxfree[0].text;

        #priceInfo =info.find("div",class_="priceInfo").find("div",class_="totalPrice").text;
        # print(flood);
        global row
        sheet.write(row, 0, title)
        sheet.write(row, 1, address)
        # sheet.write(row, 2, priceInfo)
        sheet.write(row, 3, areaetc)
        sheet.write(row, 4,area)
        sheet.write(row, 6,shitingwei)
        sheet.write(row, 7,price)
        row+=1;
        index=row;

# 判断当前运行的脚本是否是该脚本，如果是则执行
# 如果有文件xxx继承该文件或导入该文件，那么运行xxx脚本的时候，这段代码将不会执行
if __name__ == '__main__':
    # getHtml('jinshan')
    row=1
    for i in citys:
        getHtml(i)
    # 最后执行完了保存表格，参数为要保存的路径和文件名，如果不写路径则默然当前路径
    book.save('lianjia-shanghai.xls')