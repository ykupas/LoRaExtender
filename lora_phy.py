from lorawan_toa_cal import get_toa
from device import Device
import math


# LoRa PHY class
class LoRaPHY:

    # Initial characteristics
    def __init__(self):
        self.enable_auto_ldro = False
        self.enable_ldro = False
        self.enable_eh = False
        self.enable_crc = True 
        self.n_size = 11 # bytes
        self.n_sf = 10
        self.n_bw = 125 # kHz
        self.n_cr = 1
        self.n_preamble = 8 # symbols
        self.n_cadToRx = 6 # symbols
        self.n_rx1Window = 1000 # ms
        self.n_rx2Window = 2000 # ms
        self.n_accuracy = 40 # ppm
        self.n_idle_duration = 1 # ms
        self.n_cad_symbols = 16 # symbols
        self.n_resend_delay = 10000 # ms
        self._n_rxPeriodicity = 1000 # ms
        self.n_for_delay = 1000 # ms


    # Get time of air of a packet
    def ToA(self):
        toa = get_toa(self.n_size, 
                       self.n_sf, 
                       self.n_bw, 
                       self.enable_auto_ldro, 
                       self.enable_ldro, 
                       self.enable_eh, 
                       self.enable_crc, 
                       self.n_cr, 
                       self.n_preamble
                      )
        return toa['t_packet']
    

    # Get time of air of preamble
    def ToAofPreamble(self):
        toa = get_toa(self.n_size, 
                    self.n_sf, 
                    self.n_bw, 
                    self.enable_auto_ldro, 
                    self.enable_ldro, 
                    self.enable_eh, 
                    self.enable_crc, 
                    self.n_cr, 
                    self.n_preamble
                    )
        return toa['t_preamble']
    

    # Get time of air of symbol
    def ToSymb(self):
        toa = get_toa(self.n_size, 
                       self.n_sf, 
                       self.n_bw, 
                       self.enable_auto_ldro, 
                       self.enable_ldro, 
                       self.enable_eh, 
                       self.enable_crc, 
                       self.n_cr, 
                       self.n_preamble
                      )
        return toa['t_sym']
    

    # Get time of air of a packet variable in ms
    def GetToAofPacket(self, preamble, pkt_size, crc):
        if crc == True:
            self.n_cr = 1
        else:
            self.n_cr = 0
        self.n_preamble = preamble
        self.n_size = pkt_size
        return self.ToA()
    

    # Get time of air of a preamble variable
    def GetToAofPreamble(self, preamble):
        self.n_preamble = preamble
        return self.ToAofPreamble()
    

    # Calculate how many symbols in WOR preamble to reach 1 second
    def GetSymbWor1S(self):
        # Get symbol duration, divide by 1000 ms and subtract 4 of sync word
        return math.floor(1000/self.ToSymb() + 1 + 6 + self.n_cadToRx)
    

    # Calculate how many symbols in WOR preamble to reach x seconds
    def GetSymbWorXS(self, x):
        # Get symbol duration, divide by 1000 ms and subtract 4 of sync word
        return math.floor(x/self.ToSymb() + 1 + 6 + self.n_cadToRx)


    # Config LoRa phy payload size
    def SetPacketSize(self, n):
        self.n_size = n
    def GetPacketSize(self):
        return self.n_size


    # Config LoRa SF
    def SetSF(self, sf):
        self.n_sf = sf
    def GetSF(self):
        return self.n_sf


    # Config LoRa BW
    def SetBW(self, bw):
        self.n_bw = bw
    def GetBW(self):
        return self.n_bw


    # Config LoRa CR
    def SetCR(self, cr):
        self.n_cr = cr
    def GetCR(self):
        return self.n_cr


    # Config LoRa preamble
    def SetPreamble(self, preamble):
        self.n_preamble = preamble
    def GetPreamble(self):
        return self.n_preamble


    # Config LoRa packet CRC
    def EnableCRC(self):
        self.enable_crc = True
    def DisableCRC(self):
        self.enable_crc = False


    #Config RX1 window
    def SetRx1Window(self, rxWindow):
        self.n_rx1Window = rxWindow
    def GetRx1Window(self):
        return self.n_rx1Window
    
    #Config RX2 window
    def SetRx2Window(self, rxWindow):
        self.n_rx2Window = rxWindow
    def GetRx2Window(self):
        return self.n_rx1Window
    

    # Config device accuracy
    def SetAccuracy(self, accuracy):
        self.n_accuracy = accuracy
    def SetAccuracy(self):
        return self.n_accuracy
    

    # Config device RX periodicity
    def SetRxPeriodicity(self, periodicity):
        self._n_rxPeriodicity = periodicity
    def GetRxPeriodicity(self):
        return self._n_rxPeriodicity
    

    # Config other LoRa params from lib
    def EnableAutoLDRO(self):
        self.enable_auto_ldro = True
    def DisableAutoLDRO(self):
        self.enable_auto_ldro = False
    def EnableLDRO(self):
        self.enable_ldro = True
    def DisableLDRO(self):
        self.enable_ldro = False
    def EnableEH(self):
        self.enable_eh = True
    def DisableEH(self):
        self.enable_eh = False


    # Calculate drift error from two endpoints
    def GetDriftError(self, time):
        return ((self.n_accuracy + self.n_accuracy)*time)/1000000
        

    # Calculate syncronized preamble length
    def CalcPreamble(self, periodicity):
        preamble = max(8, math.floor(( (self.GetDriftError(periodicity*1000) / self.ToSymb()) + 1 + 6 + self.n_cadToRx)) )
        maxPreamble = self.GetSymbWor1S()
        if preamble < 8:
            preamble = 8
        elif preamble > maxPreamble:
            preamble = maxPreamble
        return preamble
    

    # Probability success/failed task 
    def EventGenerator(self, pdr):
        # return False
        return True