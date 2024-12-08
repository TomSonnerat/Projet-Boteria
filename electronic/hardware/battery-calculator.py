BatteryCapacityMah = 2000
LossPercentage = 10

def CalcConsumption(capacity, loss):
    TotalEnergy = (capacity / 1000) * 1.5 * 3
    EffectiveEnergy = TotalEnergy * (1 - loss / 100)
    CurrentDrawDefault = 265.62 / 1000
    CurrentDrawSleep = 105.62 / 1000
    CurrentDrawMosfet = 0.37 / 1000
    ConsumptionDefault = CurrentDrawDefault * 3.3
    ConsumptionSleep = CurrentDrawSleep * 3.3
    ConsumptionMosfet = CurrentDrawMosfet * 3.3
    LifeDefault = EffectiveEnergy / ConsumptionDefault
    LifeSleep = EffectiveEnergy / ConsumptionSleep
    LifeMosfet = EffectiveEnergy / ConsumptionMosfet
    
    return LifeDefault, LifeSleep, LifeMosfet, \
           CurrentDrawDefault * 1000, CurrentDrawSleep * 1000, CurrentDrawMosfet * 1000

def Main():
    LifeDefault, LifeSleep, LifeMosfet, \
    CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet = CalcConsumption(
        BatteryCapacityMah, LossPercentage
    )

    print(f"Case: Default")
    print(f"Current draw of: {CurrentDrawDefault} mA")
    print(f"Battery life in hours of: {LifeDefault} hours")
    print(f"Battery life in days of: {LifeDefault / 24} days")
    print()

    print(f"Case: Sleep Mode")
    print(f"Current draw of: {CurrentDrawSleep} mA")
    print(f"Battery life in hours of: {LifeSleep} hours")
    print(f"Battery life in days of: {LifeSleep / 24} days")
    print()

    print(f"Case: Sleep Mode + MOSFET")
    print(f"Current draw of: {CurrentDrawMosfet} mA")
    print(f"Battery life in hours of: {LifeMosfet} hours")
    print(f"Battery life in days of: {LifeMosfet / 24} days")

if __name__ == "__main__":
    Main()
