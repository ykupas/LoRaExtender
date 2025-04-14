class Device:
    def __init__(self):
        self.TxCurrent = 118.0
        self.RxCurrent = 5.3
        self.IdleCurrent = 0.6
        self.SleepCurrent = 0.0012
        self.Voltage = 3.3

    def SetTxCurrent(self, txCurrent):
        self.TxCurrent = txCurrent

    def GetTxCurrent(self):
        return self.TxCurrent
    
    def SetRxCurrent(self, rxCurrent):
        self.RxCurrent = rxCurrent

    def GetRxCurrent(self):
        return self.RxCurrent

    def SetIdleCurrent(self, idleCurrent):
        self.IdleCurrent = idleCurrent

    def GetIdleCurrent(self):
        return self.IdleCurrent
    
    def SetSleepCurrent(self, sleepCurrent):
        self.SleepCurrent = sleepCurrent

    def GetSleepCurrent(self):
        return self.SleepCurrent
    
    def SetVoltage(self, voltage):
        self.Voltage = voltage

    def GetVoltage(self):
        return self.Voltage
    
    # Calculate consumption in mAh with time duration variables from simulation
    def GetAppConsumption(self, totalDurationS, txDurationS, rxDurationS, idleDurationS, sleepDurationS):
        # Calculate consumption in mAh
        txConsumption = (txDurationS/3600)*self.GetTxCurrent()
        rxConsumption = (rxDurationS/3600)*self.GetRxCurrent()
        idleConsumption = (idleDurationS/3600)*self.GetIdleCurrent()
        sleepConsumption = (sleepDurationS/3600)*self.GetSleepCurrent()
        totalConsumption = txConsumption + rxConsumption + idleConsumption + sleepConsumption
        return totalConsumption, txConsumption, rxConsumption, idleConsumption, sleepConsumption
    
    # Calculate consumption in Wh with time duration variables from simulation
    def GetAppConsumptionInWh(self, totalDurationS, txDurationS, rxDurationS, idleDurationS, sleepDurationS):
        # Calculate consumption in Wh
        txConsumption = (txDurationS/3600)*(self.GetTxCurrent()/1000)*self.GetVoltage()
        rxConsumption = (rxDurationS/3600)*(self.GetRxCurrent()/1000)*self.GetVoltage()
        idleConsumption = (idleDurationS/3600)*(self.GetIdleCurrent()/1000)*self.GetVoltage()
        sleepConsumption = (sleepDurationS/3600)*(self.GetSleepCurrent()/1000)*self.GetVoltage()
        totalConsumption = txConsumption + rxConsumption + idleConsumption + sleepConsumption
        return totalConsumption, txConsumption, rxConsumption, idleConsumption, sleepConsumption
    
    # Calculate consumption in J with time duration variables from simulation
    def GetAppConsumptionInJ(self, totalDurationS, txDurationS, rxDurationS, idleDurationS, sleepDurationS):
        # Calculate consumption in Wh
        totalConsumption, txConsumption, rxConsumption, idleConsumption, sleepConsumption = \
            self.GetAppConsumptionInWh(totalDurationS, txDurationS, rxDurationS, idleDurationS, sleepDurationS)
        return totalConsumption*3600, txConsumption*3600, rxConsumption*3600, idleConsumption*3600, sleepConsumption*3600