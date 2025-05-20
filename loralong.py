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
        txtime = 0
        rxTime = 0
        idleTime = 0
        sleepTime = 0

        # First, calculate uplink event tx, rx, idle and sleep time
        # Rx long preamble uplink
        rxUpTime = self.GetToAofMessage(calcPreamble, dataLength)
        # Idle 
        idleUpTime = self.n_idle_duration
        # Sleep for RX1 to send an ACK
        sleepUpTime = self.GetRx1Window() - self.n_idle_duration
        # Tx uplink ACK
        txUpTime = self.GetToAofAck()
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep for FWD_DELAY
        sleepUpTime = sleepUpTime + self.GetFwdDelay() - self.n_idle_duration
        # Tx forwarded uplink (6 bytes of metadata)
        txUpTime = txUpTime + self.GetToAofMessage(8, dataLength + 6)
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep for RX1 to receive an ACK
        sleepUpTime = sleepUpTime + self.GetRx1Window() - self.n_idle_duration
        # Rx forwarded uplink ACK
        rxUpTime = rxUpTime + self.GetToAofAck()
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
    

    def SimulateEndpointLoRaLongPreamble(self, uplinkPeriod, dataLength, simDuration,x):

        # Calculate number of symbols of long preambles
        calcPreamble = self.GetSymbWorXS(x)
        self.SetRxPeriodicity(x)

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
    

    def SimulateRelayLoRaLongPreamble(self, uplinkPeriod, dataLength, simDuration, n, x):

        # Calculate number of symbols of long preambles
        calcPreamble = self.GetSymbWorXS(x)
        self.SetRxPeriodicity(x)
        txtime = 0
        rxTime = 0
        idleTime = 0
        sleepTime = 0

        # First, calculate uplink event tx, rx, idle and sleep time
        # Rx long preamble uplink
        rxUpTime = self.GetToAofMessage(calcPreamble, dataLength)
        # Idle 
        idleUpTime = self.n_idle_duration
        # Sleep for RX1 to send an ACK
        sleepUpTime = self.GetRx1Window() - self.n_idle_duration
        # Tx uplink ACK
        txUpTime = self.GetToAofAck()
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep for FWD_DELAY
        sleepUpTime = sleepUpTime + self.GetFwdDelay() - self.n_idle_duration
        # Tx forwarded uplink (6 bytes of metadata)
        txUpTime = txUpTime + self.GetToAofMessage(8, dataLength + 6)
        # Idle 
        idleUpTime = idleUpTime + self.n_idle_duration
        # Sleep for RX1 to receive an ACK
        sleepUpTime = sleepUpTime + self.GetRx1Window() - self.n_idle_duration
        # Rx forwarded uplink ACK
        rxUpTime = rxUpTime + self.GetToAofAck()
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