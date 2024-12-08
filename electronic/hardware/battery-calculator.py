from rich.table import Table
from rich.console import Console

def CalcConsumption(BattCapMah, Loss):
    TotalEnergy = (BattCapMah / 1000) * 1.5 * 3
    EffectiveEnergy = TotalEnergy * (1 - Loss / 100)
    CurrentDrawDefault = 265.62 / 1000
    CurrentDrawSleep = 105.62 / 1000
    CurrentDrawMosfet = 0.37 / 1000
    ConsumptionDefault = CurrentDrawDefault * 3.3
    ConsumptionSleep = CurrentDrawSleep * 3.3
    ConsumptionMosfet = CurrentDrawMosfet * 3.3
    LifeDefault = EffectiveEnergy / ConsumptionDefault
    LifeSleep = EffectiveEnergy / ConsumptionSleep
    LifeMosfet = EffectiveEnergy / ConsumptionMosfet
    
    return LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault * 1000, CurrentDrawSleep * 1000, CurrentDrawMosfet * 1000

def DisplayResults(LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet):
    FinalTable = Table(title="Battery Life Tabme", show_lines=True)
    FinalTable.add_column("Case")
    FinalTable.add_column("Current Draw (mA)")
    FinalTable.add_column("Battery Life (hours)")
    FinalTable.add_column("Battery Life (days)")
    
    FinalTable.add_row(
        "Default",
        str(CurrentDrawDefault),
        str(round(LifeDefault,2)),
        str(round(LifeDefault / 24,2))
    )
    FinalTable.add_row(
        "Sleep Mode",
        str(CurrentDrawSleep),
        str(round(LifeSleep,2)),
        str(round(LifeSleep / 24,2))
    )
    FinalTable.add_row(
        "Sleep Mode + MOSFET",
        str(CurrentDrawMosfet),
        str(round(LifeMosfet,2)),
        str(round(LifeMosfet / 24,2))
    )
    
    Console().print(FinalTable)


print("Welcome to the Battery Life Calculator, this calculator will give you an average value of the battery time you could esperate with the project according to the mode you've selected, the mode gived in the electronic-schema is the third one.")
BattCapMah = float(input("Enter the capacity of one battery cell (mAh): "))
Loss = float(input("Enter the percentage of energy lost: "))
LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet = CalcConsumption(BattCapMah, Loss)

DisplayResults(LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet)