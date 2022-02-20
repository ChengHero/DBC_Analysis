import re

class Select_signal():
    def __init__(self,dbc_path):
        try:
            self.file = open(r"{}".format(dbc_path),"r",encoding="gb18030")
            self.signal_f = self.file.readlines()
            self.file.close()
        except IOError:
            exit("DBC File Not Found")
        self.can_dbc = []
        self.Get_Meassge()  #初始化获取报文详细信息

    def Get_Signal(self,signal,value): #发送信号数据
        dbc_signal_list = []
        return_list = []
        dbc_signal_msb = None
        dbc_signal_len = None
        dbc_signal_message = None
        dbc_signal_id = None
        dbc_signal_dlc = None
        for signal_list in self.can_dbc:
            if signal in signal_list:
                signal_l = len(signal_list)
                for num in range(signal_l):
                    if signal == signal_list[num]:
                        dbc_signal_msb = int(signal_list[num+1])   #获取最高位
                        dbc_signal_len = int(signal_list[num+2])   #获取信号长度
                        dbc_signal_message = signal_list[0]    #获取报文名
                        dbc_signal_id = int(signal_list[1])     #获取ID名
                        dbc_signal_dlc = int(signal_list[2])   #获取DLC长度
                if dbc_signal_len <= 8:    #判断信号长度是否夸字节
                    offset = dbc_signal_dlc*8-(dbc_signal_msb//8+1)*8+(dbc_signal_msb-dbc_signal_len+1)%8
                else:
                    num_byte1 = (dbc_signal_msb+1)//8+1
                    switch = dbc_signal_len-(dbc_signal_msb+1)%8
                    if switch%8 !=0:    #判断剩余内容是否有余
                        num_byte2 = switch//8+1
                        diff_num = 8-switch%8
                        offset = dbc_signal_dlc*8-num_byte1*8-num_byte2*8+diff_num
                    else:
                        num_byte3 = switch//8
                        offset = dbc_signal_dlc*8-num_byte1*8-num_byte3*8

                if offset ==0:  #判断位移值
                    max_value = pow(2,dbc_signal_len ) - 1
                    if value > max_value:
                        return return_list  #数值超界，返回空列表
                    else:
                        signal_value = value
                        dbc_signal_value = hex(signal_value)   #转换成16进制
                        signal_list = dbc_signal_value.split("x")  #获取16进制内容
                        signal_diff = signal_list[1].zfill(16)
                        for list_s in range(0, 16, 2):  #按字节大小进行数据切片
                            Ds = int(signal_diff[list_s:list_s + 2], 16)    #按PCAN要求转换成10进制数据
                            dbc_signal_list.append(Ds)
                        return_list.append(dbc_signal_message)
                        return_list.append(dbc_signal_id)
                        return_list.append(dbc_signal_list)
                        return return_list

                elif offset > 0:
                    max_value = pow(2,dbc_signal_len)-1
                    if value >max_value:
                        return return_list  #数值超界，返回空列表
                    else:
                        signal_value = value << offset
                        dbc_signal_value = hex(signal_value)
                        signal_list = dbc_signal_value.split("x")
                        signal_diff = signal_list[1].zfill(16)
                        for list_s in range(0,16,2):
                            Ds = int(signal_diff[list_s:list_s+2],16)
                            dbc_signal_list.append(Ds)
                        return_list.append(dbc_signal_message)
                        return_list.append(dbc_signal_id)
                        return_list.append(dbc_signal_list)
                        return return_list
        return return_list

    def Get_signal_att(self,signal_auto):   #获取信号属性
        signal_att_list = []
        for signal_list_auto in self.can_dbc:
            if signal_auto in signal_list_auto:
                signal_l_auto = len(signal_list_auto)
                for num in range(signal_l_auto):
                    if signal_auto == signal_list_auto[num]:
                        auto_signal_len = int(signal_list_auto[num+2])   #获取信号长度
                        auto_signal_factor = int(signal_list_auto[num+3])   #获取信号长度
                        auto_signal_offset = int(signal_list_auto[num+4])   #获取信号长度
                        signal_att_list = [auto_signal_len,auto_signal_factor,auto_signal_offset]   #返回信号长度，因素，偏移量
                        return signal_att_list
        return signal_att_list

    def Get_Meassge(self):  #获取DBC报文信号数据
        can_list = []
        flag = "BO_"
        s_len = len(self.signal_f)
        for line in range(s_len):
            if flag in self.signal_f[line]:
                try:
                    can_attribute = re.compile(r"BO_ (.+?) (.+?): ([0-9])*")
                    can_attribute1 = can_attribute.findall(self.signal_f[line])
                    can_id = can_attribute1[0][0]
                    can_message = can_attribute1[0][1]
                    can_dlc = can_attribute1[0][2].strip()
                except:
                    continue
                can_list.append(can_message)
                can_list.append(can_id)
                can_list.append(can_dlc)
                num_line = line     #定义自加标志位
                flag_add = True     #定义循环标志位

                while(flag_add):    #获取信号内容
                    num_line += 1
                    if re.search("^ SG_(.+?):(.+?)\|(.+?)@.*\((.+?),(.+?)\)",self.signal_f[num_line]) !=None:
                        signal_value = self.signal_f[num_line]
                        signal_attribute = re.compile("^ SG_(.+?):(.+?)\|(.+?)@.*\((.+?),(.+?)\)")
                        signal_attribute1 = signal_attribute.findall(signal_value)
                        signal = signal_attribute1[0]
                        can_list.append(signal[0].strip())
                        can_list.append(signal[1].strip())
                        can_list.append(signal[2].strip())
                        can_list.append(signal[3].strip())
                        can_list.append(signal[4].strip())
                    elif self.signal_f[num_line].strip() == "":  #遇到空行跳出循环
                        self.can_dbc.append(can_list)
                        can_list = []
                        flag_add = False

