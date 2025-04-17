from lora_phy import LoRaPHY


# LoRaWAN class from LoRaPHY
class LoRaWAN(LoRaPHY):

    # Initial variables
    def __init__(self, pckt, sf, bw, cr):
        super().__init__()
        self.EnableCRC()
        self.SetCR(cr)
        self.SetBW(bw)
        self.SetSF(sf)
        self.SetPacketSize(pckt)
        self.SetPreamble(8)
        self.SetRx1Window(1000)
        self.SetRx2Window(2000)
        self.n_wor_delay = 50


    # Get time of air of a WOR ACK packet (tabled)
    def GetToAofWorAck(self):
        toa = 0
        if self.n_sf == 7 and self.n_bw == 125:
            toa = 36
        elif self.n_sf == 7 and self.n_bw == 250:
            toa = 27.2
        elif self.n_sf == 7 and self.n_bw == 500:
            toa = 9
        elif self.n_sf == 8 and self.n_bw == 125:
            toa = 72.1
        elif self.n_sf == 8 and self.n_bw == 250:
            toa = 36
        elif self.n_sf == 8 and self.n_bw == 500:
            toa = 18
        elif self.n_sf == 9 and self.n_bw == 125:
            toa = 123.9
        elif self.n_sf == 9 and self.n_bw == 250:
            toa = 61.9
        elif self.n_sf == 9 and self.n_bw == 500:
            toa = 30.9
        elif self.n_sf == 10 and self.n_bw == 125:
            toa = 247.8
        elif self.n_sf == 10 and self.n_bw == 250:
            toa = 123.9
        elif self.n_sf == 10 and self.n_bw == 500:
            toa = 61.9
        elif self.n_sf == 11 and self.n_bw == 125:
            toa = 495.6
        elif self.n_sf == 11 and self.n_bw == 250:
            toa = 247.8
        elif self.n_sf == 11 and self.n_bw == 500:
            toa = 123.9
        elif self.n_sf == 11 and self.n_bw == 125:
            toa = 991.2
        elif self.n_sf == 11 and self.n_bw == 250:
            toa = 495.6
        elif self.n_sf == 12 and self.n_bw == 500:
            toa = 247.8
        return toa
    

    # Get time of air from WOR with variable preamble
    def GetToAofWor(self, preamble):
        # 15 bytes (1 hdr + 14 uplink WOR data)
        return self.GetToAofPacket(preamble, 15, True)


    # Get time of air of a uplink with variable packet size
    def GetToAofUplink(self, pkt_size):
        return self.GetToAofPacket(8, pkt_size, True)
    

    # Get time of air of a downlink with variable packet size
    def GetToAofDownlink(self, pkt_size):
        return self.GetToAofPacket(8, pkt_size, False)


    # Get time of air of a uplink ACK packet
    def GetToAofUplinkAck(self):
        return self.GetToAofDownlink(0)
    

    # Get WORtoACK/WORACKtoUplink delay
    def GetWorDelay(self):
        return self.n_wor_delay
    
    
    #Config RX1 window
    def SetRxRWindow(self, rxWindow):
        self.n_rxrWindow = rxWindow
    def GetRxRWindow(self):
        return self.n_rxrWindow
    

    #########################################################################################
    # Simulate a endpoint LoRaWAN one-hop relay network confirmed uplink from endpoint
    #
    # self -> object to handle endpoint state
    # upPeriodicity -> periodicity of application in seconds
    # dataLength -> size in bytes of application payload
    # simDuration -> simulation duration in seconds
    #
    # ret -> txDuration, rxDuration, idleDuration, sleepDuration
    #
    #########################################################################################
    def SimulateEndpointLoRaWAN(self, uplinkPeriod, dataLength, simDuration):

        # Calculate number of symbols of long preambles
        calcPreamble = self.CalcPreamble(uplinkPeriod)
        # print("Calculated preamble size: ", calcPreamble)

        #### Uplink ṕrocess ####
        event = 0

        # Calculate every TX in uplink process
        # Wor send
        worSendTime = self.GetToAofWor(calcPreamble)
        event = event + 1
        # Up send
        uplinkSendTime = self.GetToAofUplink(dataLength)
        event = event + 1
        # Tx total
        txTime = worSendTime + uplinkSendTime

        # Calculate every RX in uplink process
        # Wor Ack receive
        worAckReceiveTime = self.GetToAofWorAck()
        event = event + 1
        # Up Ack receive
        uplinkAckReceiveTime = self.GetToAofUplinkAck()
        event = event + 1
        # Rx Total
        rxTime = worAckReceiveTime + uplinkAckReceiveTime

        # Calculate every idle in uplink process
        # Number of times an event happend
        idleTime = event * self.n_idle_duration

        # Calculate sleep in rest of upPeriod time
        # upPeriod is full period time, less what already happened
        sleepTime = uplinkPeriod*1000 - (txTime + rxTime + idleTime)

        # Calculate how many upPeriods is in simDuration
        nUp = simDuration/uplinkPeriod

        # Calculate total tx, rx, idle and sleep time with nUp
        txDuration = txTime*nUp/1000
        rxDuration = rxTime*nUp/1000
        idleDuration = idleTime*nUp/1000
        sleepDuration = sleepTime*nUp/1000

        return txDuration, rxDuration, idleDuration, sleepDuration
    

    #########################################################################################
    # Simulate of a relay in LoRaWAN network confirmed uplink
    #
    # self -> object to handle endpoint state
    # uplinkPeriod -> periodicity of applicaion uplink in seconds
    # dataLength -> size in bytes of application payload
    # simDuration -> simulation duration in seconds
    # N -> number o endpoints connected to simuled relay
    #
    # ret -> txDuration, rxDuration, idleDuration, sleepDuration
    #
    #########################################################################################
    def SimulateRelayLoRaWAN(self, uplinkPeriod, dataLength, simDuration, n):

        # Calculate number of symbols of long preambles
        calcPreamble = self.CalcPreamble(uplinkPeriod)
        # print("Calculated preamble size: ", calcPreamble)

        # First, calculate uplink tx, rx, idle and sleep time
        # Total TX time in uplink
        worAckSendTime = self.GetToAofWorAck()
        upFwdSendTime = self.GetToAofUplink(dataLength + 6)
        uplinkAckSendTime = self.GetToAofUplinkAck()
        txUpTime = worAckSendTime + upFwdSendTime + uplinkAckSendTime
        # Total RX time in uplink
        worReceiveTime = self.GetToAofWor(calcPreamble)
        uplinkReceiveTime = self.GetToAofUplink(dataLength)
        upFwdAckReceiveTime = self.GetToAofUplinkAck()
        rxUpTime = worReceiveTime + uplinkReceiveTime + upFwdAckReceiveTime
        # Total Idle time in uplink (6 events of tx and rx)
        idleUpTime = 6 * self.n_idle_duration
        # Until end of endpoint task Sleep time
        sleepUpTime = 2*self.GetWorDelay() + 3*self.GetRx1Window() - idleUpTime
        # Calculate the remaining of slot of rxPeriodicity time, and sum it to Sleep time
        sleepRemainTime = self._n_rxPeriodicity - ((txUpTime + rxUpTime + idleUpTime + sleepUpTime) % self._n_rxPeriodicity)
        sleepUpTime = sleepUpTime + sleepRemainTime
        # Calculate total uplink event time
        upTime = txUpTime + rxUpTime + idleUpTime + sleepUpTime

        # Second, calculate Cad event time
        rxCadEventTime = self.ToSymb() * self.n_cad_symbols
        idleCadEventTime = self.n_idle_duration
        sleepCadEventTime = self._n_rxPeriodicity - (rxCadEventTime + self.n_idle_duration)

        # # REVER TODO:

        # # Third, count how many Uplinks and Cads happen
        # cadInUp = ((uplinkPeriod)*n - upTime)//self._n_rxPeriodicity        
        # txTotalEventTime = txUpTime
        # rxTotalEventTime = rxUpTime + cadInUp*rxCadEventTime
        # idleTotalEventTime = idleUpTime + cadInUp*idleCadEventTime
        # sleepTotalEventTime = sleepUpTime + cadInUp*sleepCadEventTime      

        # # Finally, calculate total tx, rx, idle and sleep in seconds
        # nUplinksEvents = simDuration/(uplinkPeriod/n)
        # txDuration = nUplinksEvents*txTotalEventTime/1000
        # rxDuration = nUplinksEvents*rxTotalEventTime/1000
        # idleDuration = nUplinksEvents*idleTotalEventTime/1000
        # sleepDuration = nUplinksEvents*sleepTotalEventTime/1000

        # Return tx, rx, idle and sleep duration
        return txDuration, rxDuration, idleDuration, sleepDuration