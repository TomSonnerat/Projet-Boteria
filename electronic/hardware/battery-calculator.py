from rich.table import Table
from rich.console import Console
from dataclasses import dataclass

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
    finaletext = frame.top_left + frame.top * txtlen + frame.top_right + '\n'
    for line in txt:
        finaletext += frame.left + line + ((txtlen - len(line)) * ' ') + frame.right + '\n'
    finaletext += frame.bottom_left + frame.top * txtlen + frame.bottom_right
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
        "Default", str(CurrentDrawDefault), str(round(LifeDefault, 2)), str(round(LifeDefault / 24, 2))
    )
    FinalTable.add_row(
        "Sleep Mode", str(CurrentDrawSleep), str(round(LifeSleep, 2)), str(round(LifeSleep / 24, 2))
    )
    FinalTable.add_row(
        "Sleep Mode + MOSFET", str(CurrentDrawMosfet), str(round(LifeMosfet, 2)), str(round(LifeMosfet / 24, 2))
    )
    
    Console().print(FinalTable)

def GetBatteryCapacity():
    while True:
        try:
            capacity = input("Enter the capacity of one battery cell (mAh) or press enter for default value (2000 mAh): ")
            if capacity == "":
                return 2000
            capacity_float = float(capacity)
            if 500 <= capacity_float <= 3500:
                return capacity_float
            else:
                print("Error: Capacity must be between 500 and 3500 mAh")
        except ValueError:
            print("Invalid input. Please enter a numeric value")

def GetEnergyLoss():
    print("\nEnergy Loss Percentage:")
    print("1: 5%")
    print("2: 10% (default)")
    print("3: 15%")
    print("4: Custom")
    
    while True:
        try:
            choice = input("Choose an option (1-4): ")
            
            if choice == "" or choice == "2":
                return 10
            elif choice == "1":
                return 5
            elif choice == "3":
                return 15
            elif choice == "4":
                while True:
                    try:
                        custom_loss = float(input("Enter custom energy loss percentage: "))
                        return custom_loss
                    except ValueError:
                        print("Invalid input. Please enter a numeric value")
            else:
                print("Invalid option. Please choose 1, 2, 3, or 4")
        except ValueError:
            print("Invalid input.")

def main():
    print(frame_text("DESCRIPTION: \n" + ('-' * 40) + "\n" +
                     "Welcome to the Battery Life Calculator\n" +
                     "This calculator will give you an average value of the battery time\n" +
                     "you could expect with the project according to the mode you've selected.\n" +
                     "The mode given in the electronic schema is the third one.", fancy_frame))
    
    print('-' * 40 + '\nVariables:')
    
    BattCapMah = GetBatteryCapacity()
    Loss = GetEnergyLoss()
    
    print('-' * 40)
    
    LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet = CalcConsumption(BattCapMah, Loss)
    DisplayResults(LifeDefault, LifeSleep, LifeMosfet, CurrentDrawDefault, CurrentDrawSleep, CurrentDrawMosfet)

if __name__ == "__main__":
    main()