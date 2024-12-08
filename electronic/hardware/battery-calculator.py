from rich.table import Table
from rich.console import Console
from dataclasses import dataclass, replace

@dataclass
class Frame:
    top: str = "-"
    left: str = "|"
    bottom: str = "-"
    right: str = "|"
    top_left: str = "+"
    top_right: str = "+"
    bottom_left: str = "+"
    bottom_right: str = "+"

fancy_frame = Frame("─", "│", "─", "│", "╭", "╮", "╰", "╯")

def frame_text(text: str, frame: Frame):
    txt = text.split('\n')
    txtlen = max([len(data) for data in txt])
    finaletext = frame.top_left+frame.top*txtlen+frame.top_right+'\n'
    for line in txt:
        finaletext += frame.left+line+((txtlen-len(line))*' ')+frame.right+'\n'
    finaletext += frame.bottom_left+frame.top*txtlen+frame.bottom_right
    return finaletext

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
    FinalTable = Table(title="Battery Life Table", show_lines=True)
    FinalTable.add_column("Case", style="cyan", justify="center")
    FinalTable.add_column("Current Draw (mA)", style="green", justify="center")
    FinalTable.add_column("Battery Life (hours)", style="magenta", justify="center")
    FinalTable.add_column("Battery Life (days)", style="yellow", justify="center")
    
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

print(frame_text("DESCRIPTION: \n"+('-'*40)+"\nWelcome to the Battery Life Calculator\nthis calculator will give you an average value of the battery time\nyou could esperate with the project according to the mode you've selected,\nthe mode gived in the electronic-schema is the third one.", fancy_frame))

print('-'*40+'\nVariables:')

BattCapMah = float(input("Enter the capacity of one battery cell (mAh): "))
Loss = float(input("Enter the percentage of energy lost: "))

print('-'*40)

LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet = CalcConsumption(BattCapMah, Loss)

DisplayResults(LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet)