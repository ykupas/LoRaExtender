from lora_phy import LoRaPHY

class LoRaExtensor(LoRaPHY):
    def __init__(self, pckt, sf, bw, cr):
        super().__init__()
        self.EnableCRC()
        self.SetCR(cr)
        self.SetBW(bw)
        self.SetSF(sf)
        self.SetPreamble(8)
        self.SetPacketSize(pckt)
        self.SetRx1Window(1000)

    def GetToAofDataMessage(self, pkt_size):
        return self.GetToAofPacket(8, pkt_size, True)
    
    def GetToAofAckMessage(self):
        return self.GetToAofPacket(8, 0, False)
    
    def SimulateEndpointLoRaExtensor(self, uplinkPeriod, dataLength, simDuration):

        #### Uplink ṕrocess ####
        event = 0

        # Calculate every TX in uplink process
        # Data send
        dataSendTime = self.GetToAofDataMessage(dataLength)
        event = event + 1
        # Tx total
        txTime = dataSendTime

        # Calculate every RX in uplink process
        # Data Ack receive
        dataAckReceiveTime = self.GetToAofAckMessage()
        event = event + 1
        # Rx Total
        rxTime = dataAckReceiveTime

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