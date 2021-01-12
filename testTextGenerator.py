import os
import time
import random


# 生成指定大小的TXT档
def generateTXTFile():
    fileNum = 1
    fileSize = 0
    # 判断输入是否有误
    while True:
        inputNum = input('请输入你想生成的TXT文件数量:')
        inputSize = input('请输入你想生成的TXT文件大小(MB):')
        if inputSize.strip().isdigit() and inputNum.strip().isdigit() != True:
            print('只能输入整数，请重新输入!')
            continue
        else:
            fileNum = int(inputNum)
            fileSize = int(inputSize)
            break
    if fileSize >= 200:
        print('正在生成TXT文件，请稍候... ...')
    todayDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # 设置文件保存路径
    catelogPath = os.getcwd()
    # 获取开始时间，比 time.time()准确
    startTime = time.perf_counter()
    for i in range(1, fileNum+1):
        oneFileSize = 0
        fileName = todayDate + '_' + str(fileNum) + 'MB' + '_' + str(i) + '.txt'
        filePath = catelogPath + '/' + str(fileSize) 
        temporaryFilePath = filePath + '/' +fileName
        # 目录不存在就创建目录
        if not os.path.exists(filePath):
            os.mkdir(filePath)
        with open(temporaryFilePath, 'w', encoding="utf8") as f:
            while fileSize * 1024 * 1024 >= oneFileSize:
                try:
                    # 写入字符，写入固定字符效率高点
                    # f.write(str(round(random.uniform(-1000, 1000), 2) * 1024)) 
                    f.write('01'* 100) 
                    oneFileSize = os.path.getsize(temporaryFilePath)
                except KeyboardInterrupt:
                    print(f'异常中断:{KeyboardInterrupt}')
            f.close
        print(f'生成第 {i} 个 {fileSize}M 文本')
    # 获取结束时间
    endTime = time.perf_counter()
    print(f'文件已成生并保存, 文件数量: {fileNum} 个, 文件大小:{fileSize}MB')
    print(f'保存路径: {catelogPath}')
    print(f'总共耗时:{endTime - startTime}')


if __name__ == '__main__':
    generateTXTFile()