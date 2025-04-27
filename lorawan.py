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
        elif self.n_sf == 12 and self.n_bw == 125:
            toa = 991.2
        elif self.n_sf == 12 and self.n_bw == 250:
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
    # uplinkPeriod -> periodicity of application in seconds
    # dataLength -> size in bytes of application payload
    # simDuration -> simulation duration in seconds
    #
    # ret -> txDuration, rxDuration, idleDuration, sleepDuration
    #
    #########################################################################################
    def SimulateEndpointLoRaWAN(self, uplinkPeriod, dataLength, simDuration):

        # Calculate number of symbols of long preambles
        calcPreamble = self.CalcPreamble(uplinkPeriod)
        txtime = 0
        rxTime = 0
        idleTime = 0
        sleepTime = 0

        # Calculate uplink event tx, rx, idle, sleep tim
        # Tx WOR
        txTime = self.GetToAofWor(calcPreamble)
        # Idle 
        idleTime = self.n_idle_duration
        # Sleep WOR_ACK_DELAY
        sleepTime = self.GetWorDelay() - self.n_idle_duration
        # Rx WOR ACK
        rxTime = self.GetToAofWorAck()
        # Idle 
        idleTime = idleTime + self.n_idle_duration
        # Sleep WOR_DATA_DELAY
        sleepTime = sleepTime + self.GetWorDelay() - self.n_idle_duration
        # Tx uplink
        txTime = txTime + self.GetToAofUplink(dataLength)
        # Idle
        idleTime = idleTime + self.n_idle_duration
        # Sleep RX1 window (same as wait for forward uplink and receive ack in RXR)
        sleepTime = sleepTime + self.GetWorDelay() - self.n_idle_duration
        # Rx uplink ACK
        rxTime = rxTime + self.GetToAofUplinkAck()
        # Idle
        idleTime = idleTime + self.n_idle_duration
        # Sleep rest of uplink slot of periodicity 
        sleepTime = sleepTime + uplinkPeriod*1000 - (txTime + rxTime + idleTime)
        
        # Calculate how many upPeriods is in simDuration
        nUp = simDuration//uplinkPeriod
        sleepTime = sleepTime + (simDuration % uplinkPeriod)

        # Calculate total tx, rx, idle and sleep time with nUp
        txDuration = txTime*nUp/1000
        rxDuration = rxTime*nUp/1000
        idleDuration = idleTime*nUp/1000
        sleepDuration = sleepTime*nUp/1000

        return txDuration, rxDuration, idleDuration, sleepDuration
    

    #########################################################################################
    # Simulate a endpoint LoRaWAN one-hop relay network confirmed uplink from endpoint
    #
    # self -> object to handle endpoint state
    # uplinkPeriod -> periodicity of application in seconds
    # dataLength -> size in bytes of application payload
    # simDuration -> simulation duration in seconds
    #
    # ret -> txDuration, rxDuration, idleDuration, sleepDuration
    #
    #########################################################################################
    def SimulateEndpointUnconfirmedLoRaWAN(self, uplinkPeriod, dataLength, simDuration):

        # Calculate number of symbols of long preambles
        calcPreamble = self.CalcPreamble(uplinkPeriod)
        txtime = 0
        rxTime = 0
        idleTime = 0
        sleepTime = 0

        # Calculate uplink event tx, rx, idle, sleep tim
        # Tx WOR
        txTime = self.GetToAofWor(calcPreamble)
        # Idle 
        idleTime = self.n_idle_duration
        # Sleep WOR_ACK_DELAY
        sleepTime = self.GetWorDelay() - self.n_idle_duration
        # Rx WOR ACK
        rxTime = self.GetToAofWorAck()
        # Idle 
        idleTime = idleTime + self.n_idle_duration
        # Sleep WOR_DATA_DELAY
        sleepTime = sleepTime + self.GetWorDelay() - self.n_idle_duration
        # Tx uplink
        txTime = txTime + self.GetToAofUplink(dataLength)
        # Idle
        idleTime = idleTime + self.n_idle_duration
        # Sleep rest of uplink slot of periodicity 
        sleepTime = sleepTime + uplinkPeriod*1000 - (txTime + rxTime + idleTime)
        
        # Calculate how many upPeriods is in simDuration
        nUp = simDuration//uplinkPeriod
        sleepTime = sleepTime + (simDuration % uplinkPeriod)

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
    def SimulateRelayConfirmedLoRaWAN(self, uplinkPeriod, dataLength, simDuration, n):

        # Calculate number of symbols of long preambles
        calcPreamble = self.CalcPreamble(uplinkPeriod)
        txtime = 0
        rxTime = 0
        idleTime = 0
        sleepTime = 0

        # First, calculate uplink event tx, rx, idle and sleep time
        # Rx WOR
        rxUpTime = self.GetToAofWor(calcPreamble)
        # Idle 
        idleUpTime = self.n_idle_duration
        # Sleep WOR_ACK_DELAY
        sleepUpTime = self.GetWorDelay() - self.n_idle_duration
        # Tx WOR ACK
        txUpTime = self.GetToAofWorAck()
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep WOR_DATA_DELAY
        sleepUpTime = sleepUpTime + self.GetWorDelay() - self.n_idle_duration
        # Rx Uplink
        rxUpTime = rxUpTime + self.GetToAofUplink(dataLength)
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep RELAY_FWD_DELAY = WOR_DATA_DELAY = WOR_ACK_DELAY
        sleepUpTime = sleepUpTime + self.GetWorDelay() - self.n_idle_duration
        # Tx Forward uplink
        txUpTime = txUpTime + self.GetToAofUplink(dataLength + 6)
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep RX1_DELAY
        sleepUpTime = sleepUpTime + self.GetRx1Window() - self.n_idle_duration
        # Rx Forward uplink ACK
        rxUpTime = rxUpTime + self.GetToAofUplinkAck()
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep RX1_DELAY
        sleepUpTime = sleepUpTime + self.GetRx1Window() - self.n_idle_duration
        # Tx Uplink ACK
        txUpTime = txUpTime + self.GetToAofUplinkAck()
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Calculate the remaining of slot of rxPeriodicity time, and sum it to Sleep time
        upTotalTime = txUpTime + rxUpTime + idleUpTime + sleepUpTime
        sleepRemainTime = self._n_rxPeriodicity - (upTotalTime % self._n_rxPeriodicity)
        # Sum remain sleep time and resum uplink event total time
        sleepUpTime = sleepUpTime + sleepRemainTime
        upTotalTime = txUpTime + rxUpTime + idleUpTime + sleepUpTime

        # Second, calculate Cad event rx, idle and sleep time
        rxCadTime = self.ToSymb() * self.n_cad_symbols
        idleCadTime = self.n_idle_duration
        sleepCadTime = self._n_rxPeriodicity - (rxCadTime + self.n_idle_duration)

        # Third, count how many Uplinks and Cads happen
        nUpEvents = (simDuration/uplinkPeriod)*n
        nCadEvents = ( simDuration*1000 - nUpEvents*(upTotalTime) ) // self._n_rxPeriodicity
        sleepTotalRemainTime = ( simDuration*1000 - nUpEvents*(upTotalTime) ) % self._n_rxPeriodicity

        # Fourth, calculate the time spent in each state with uplink and cad events number
        txTime = nUpEvents*txUpTime
        rxTime = nUpEvents*rxUpTime + nCadEvents*rxCadTime
        idleTime = nUpEvents*idleUpTime + nCadEvents*idleCadTime
        sleepTime = nUpEvents*sleepUpTime + nCadEvents*sleepCadTime + sleepTotalRemainTime

        # Finally, calculate total tx, rx, idle and sleep in seconds
        txDuration = txTime/1000
        rxDuration = rxTime/1000
        idleDuration = idleTime/1000
        sleepDuration = sleepTime/1000

        # Return tx, rx, idle and sleep duration
        return txDuration, rxDuration, idleDuration, sleepDuration
    

    #########################################################################################
    # Simulate of a relay in LoRaWAN network unconfirmed uplink
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
    def SimulateRelayUnconfirmedLoRaWAN(self, uplinkPeriod, dataLength, simDuration, n):

        # Calculate number of symbols of long preambles
        calcPreamble = self.CalcPreamble(uplinkPeriod)
        txtime = 0
        rxTime = 0
        idleTime = 0
        sleepTime = 0

        # First, calculate uplink event tx, rx, idle and sleep time
        # Rx WOR
        rxUpTime = self.GetToAofWor(calcPreamble)
        # Idle 
        idleUpTime = self.n_idle_duration
        # Sleep WOR_ACK_DELAY
        sleepUpTime = self.GetWorDelay() - self.n_idle_duration
        # Tx WOR ACK
        txUpTime = self.GetToAofWorAck()
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep WOR_DATA_DELAY
        sleepUpTime = sleepUpTime + self.GetWorDelay() - self.n_idle_duration
        # Rx Uplink
        rxUpTime = rxUpTime + self.GetToAofUplink(dataLength)
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep RELAY_FWD_DELAY
        sleepUpTime = sleepUpTime + self.GetWorDelay() - self.n_idle_duration
        # Tx Forward uplink
        txUpTime = txUpTime + self.GetToAofUplink(dataLength + 6)
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Calculate the remaining of slot of rxPeriodicity time, and sum it to Sleep time
        upTotalTime = txUpTime + rxUpTime + idleUpTime + sleepUpTime
        sleepRemainTime = self._n_rxPeriodicity - (upTotalTime % self._n_rxPeriodicity)
        # Sum remain sleep time and resum uplink event total time
        sleepUpTime = sleepUpTime + sleepRemainTime
        upTotalTime = txUpTime + rxUpTime + idleUpTime + sleepUpTime

        # Second, calculate Cad event rx, idle and sleep time
        rxCadTime = self.ToSymb() * self.n_cad_symbols
        idleCadTime = self.n_idle_duration
        sleepCadTime = self._n_rxPeriodicity - (rxCadTime + self.n_idle_duration)

        # Third, count how many Uplinks and Cads happen
        nUpEvents = (simDuration/uplinkPeriod)*n
        nCadEvents = ( simDuration*1000 - nUpEvents*(upTotalTime) ) // self._n_rxPeriodicity
        sleepTotalRemainTime = ( simDuration*1000 - nUpEvents*(upTotalTime) ) % self._n_rxPeriodicity

        # Fourth, calculate the time spent in each state with uplink and cad events number
        txTime = nUpEvents*txUpTime
        rxTime = nUpEvents*rxUpTime + nCadEvents*rxCadTime
        idleTime = nUpEvents*idleUpTime + nCadEvents*idleCadTime
        sleepTime = nUpEvents*sleepUpTime + nCadEvents*sleepCadTime + sleepTotalRemainTime

        # Finally, calculate total tx, rx, idle and sleep in seconds
        txDuration = txTime/1000
        rxDuration = rxTime/1000
        idleDuration = idleTime/1000
        sleepDuration = sleepTime/1000

        # Return tx, rx, idle and sleep duration
        return txDuration, rxDuration, idleDuration, sleepDuration