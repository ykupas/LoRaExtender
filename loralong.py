from lora_phy import LoRaPHY

class LoRaLong(LoRaPHY):
    def __init__(self, pckt, sf, bw, cr):
        super().__init__()
        self.EnableCRC()
        self.SetCR(cr)
        self.SetBW(bw)
        self.SetSF(sf)
        self.SetPreamble(116)
        self.SetPacketSize(pckt)
        self.SetRx1Window(1000)
        self.fwd_delay = 1000

    def GetToAofMessage(self, preamble, pkt_size):
        return self.GetToAofPacket(preamble, pkt_size, True)


    def GetToAofAck(self):
        return self.GetToAofPacket(8, 0, False)
    

    def GetFwdDelay(self):
        return self.fwd_delay
    

    def SimulateEndpointLoRaLong(self, uplinkPeriod, dataLength, simDuration):

        # Calculate number of symbols of long preambles
        calcPreamble = self.GetSymbWor1S()

        #### Uplink ṕrocess ####
        event = 0

        # Calculate every TX in uplink process
        # Long preamble uplink send
        longUpSend = self.GetToAofMessage(calcPreamble, dataLength)
        event = event + 1
        # Tx total
        txTime = longUpSend

        # Calculate every RX in uplink process
        # Up Ack receive
        upAckReceiveTime = self.GetToAofAck()
        event = event + 1
        # Rx Total
        rxTime = upAckReceiveTime

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
    

    def SimulateRelayLoRaLong(self, uplinkPeriod, dataLength, simDuration, n):

        # Calculate number of symbols of long preambles
        calcPreamble = self.GetSymbWor1S()
        # print("Calculated preamble size: ", calcPreamble)

        # First, calculate uplink tx, rx, idle and sleep time
        # Total TX time in uplink
        upAckSendTime = self.GetToAofAck()
        upFwdSendTime = self.GetToAofMessage(8, dataLength + 6)
        txUpTime = upAckSendTime + upFwdSendTime
        # Total RX time in uplink
        longUpReceiveTime = self.GetToAofMessage(calcPreamble, dataLength)
        upFwdAckReceiveTime = self.GetToAofAck()
        rxUpTime = longUpReceiveTime + upFwdAckReceiveTime
        # Total Idle time in uplink (4 events of tx and rx)
        idleUpTime = 4 * self.n_idle_duration
        # Until end of endpoint task Sleep time
        sleepUpTime = self.GetFwdDelay() + 2*self.GetRx1Window() - idleUpTime
        # Calculate the remaining of slot of rxPeriodicity time, and sum it to Sleep time
        sleepRemainTime = self._n_rxPeriodicity - ((txUpTime + rxUpTime + idleUpTime + sleepUpTime) % self._n_rxPeriodicity)
        sleepUpTime = sleepUpTime + sleepRemainTime
        # Calculate total uplink event time
        upTime = txUpTime + rxUpTime + idleUpTime + sleepUpTime

        # Second, calculate how many Cad events has in the remaining of upPeriod
        cadInUp = (((uplinkPeriod/n)*1000) - upTime)/self._n_rxPeriodicity
        rxCadEventTime = cadInUp*(self.ToSymb() * self.n_cad_symbols)
        idleCadEventTime = cadInUp*(self.n_idle_duration)
        sleepCadEventTime = cadInUp*(self._n_rxPeriodicity - (self.ToSymb() * self.n_cad_symbols + self.n_idle_duration))

        # Third, calculate in geral event (up + cad) all times
        txTotalEventTime = txUpTime
        rxTotalEventTime = rxUpTime + rxCadEventTime
        idleTotalEventTime = idleUpTime + idleCadEventTime
        sleepTotalEventTime = sleepUpTime + sleepCadEventTime

        # Forth, calculate how many uplink are in simulation with n endpoints connected
        nUplinksEvents = (simDuration/uplinkPeriod)*n

        # Finally, calculate total tx, rx, idle and sleep in seconds
        txDuration = nUplinksEvents*txTotalEventTime/1000
        rxDuration = nUplinksEvents*rxTotalEventTime/1000
        idleDuration = nUplinksEvents*idleTotalEventTime/1000
        sleepDuration = nUplinksEvents*sleepTotalEventTime/1000

        # Return tx, rx, idle and sleep duration
        return txDuration, rxDuration, idleDuration, sleepDuration