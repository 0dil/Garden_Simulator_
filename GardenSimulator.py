import sys
try:
    # for Python2
    from tkinter import *
except ImportError:
    # for Python3
    from tkinter import *


class ToolTip(object):

    def __init__(self, widget):
        self.wraplength = 180
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self):
        # Display text in tooltip window
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "10", "normal"),
                      wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def settext(self, text):
        self.text = text

def createToolTip(widget, text):
    toolTip = ToolTip(widget)
    toolTip.settext(text)
    def enter(event):
        toolTip.showtip()
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
    return toolTip



# Set Window items
root = Tk()
root.geometry("560x320")
root.title("Garden Simulator")

# Initialize variables
# All plants
PLANTS = [
    "-",     
    "Лук",  
    "Огурец",   
    "Морков",   
    "Чеснок",   
    "Помидор",   
    "Кукуруза",   
    "Баклажан",   
    "Картошка",   
    "Перец",   
    "Свёкла",   
    "Капуста",   
    "Брокколи",   
    "Имбирь",   
    "Редис",   
    "Горох",   
    "Кабачок",   
    "Тыква",   
    "Яблоко",   
    "Груша",   
    "Лимон",   
    "Арбуз",   
    "Дыня",   
    "Слива",   
    "Клубника",   
    "Апельсин",  
    "Виноград",  
    "Ананас",  
    "Киви",  
    "Хурма",  
    "Гранат", 
    "Вишня",  
    "Банан",  
    "Абрикос",  
    "Черешня"   
]



# All plant effects
EFFECTS = [
    "",                 # 0
    "CpS, Sun",
    "CpC, Sun",    
    "Cursor CpS, Rain",
    "Grandma CpS, Rain",
    "Rand Drops, Rain",       # 5
    "Milk Effect, Sun",
    "Reindeer Gains, Rain",
    "Reindeer Freq, Sun",
    "Drought, Sun",
    "GC Gains, Sun",         # 10
    "GC Effect Length, Rain",
    "GC Freq, Sun",
    "GC Duration, Sun",
    "WC Gains, Drought",
    "WC Freq, Drought",          # 15
    "WC Chance, Sun",
    "Wrinkler Spawn, Rain",
    "Wrinkler Digenstion, Drought"
]

# Encoded list of effects per plant
# Each element represents a plant in the PLANTS list, as a list
# first list inside is the effect from EFFECTS list
# second list is the magnitude of each effect, as a %
PLANTEFFECTS = [
    [[],[]],
    [[1],[1]],
    [[2],[2]],
    [[4],[3]],
    [[10,11],[1,0.1]],
    [[12],[1]],
    [[12],[3]],
    [[10,12,5],[1,1,1]],
    [[14,15,4],[1,1,1]],
    [[1],[1]],
    [[1],[1]],
    [[10],[1]],
    [[],[]],
    [[6],[0.2]],
    [[7,8],[1,1]],
    [[1],[-2]],
    [[1,2,12],[3,-5,-10]],
    [[16,17],[-2,-15]],
    [[5],[3]],
    [[11,1],[0.3,-2]],
    [[1],[-10]],
    [[],[]],
    [[1],[-2]],
    [[],[]],
    [[],[]],
    [[1],[1]],
    [[1],[-1]],
    [[],[]],
    [[],[]],
    [[2,3,1],[4,1,-1]],
    [[9],[-0.2]],
    [[12,10,13,11],[2,-5,-2,-2]],
    [[17,18],[2,1]],
    [[13,12,5],[0.5,1,1]],
    [[],[]]
]

# types of useful plants
SOILS = [
    ("Базилик",1),
    ("Мята",2),
    ("Лаванда",3),
    ("Лимонная трава",4),
    ("Розмарин",5)
]

# soil effects
SOILEFFECTS = [0,1,0.75,1.25,0.25,0.25]
SOILWEEDS = [0,1,1.2,1,0.1,0.1]

soil = IntVar()
soil.set(1)
gardenTiles = [ StringVar() for i in range(36)]
for i in range(36):
    gardenTiles[i].set(PLANTS[0])

gardenFill = StringVar()
gardenFill.set(PLANTS[0])
plotEffects = [1] * 36
plotAging = [1] * 36
plotFungus = [1] * 36

# Initialize functions
def AddBoost(c, s, m, plotEffects):
    # center, size, magnitude
    x = c // 6
    y = c % 6
    for i in range(max(x - s, 0), min(x + s + 1, 6)):
        for j in range(max(y - s, 0), min(y + s + 1, 6)):
            if i!=x or j!=y:
                e = plotEffects[i * 6 + j]
                plotEffects[i * 6 + j] = m * e
    return plotEffects

def NormalizeMult(boost, mult):
    newBoost = boost
    if boost >= 1:
        newBoost = (boost-1)*mult+1
    elif mult >= 1:
        newBoost = 1/((1/boost)*mult)
    else:
        newBoost = 1-(1-boost)*mult
    return newBoost

def RecalcPlotBoost():
    # This is the actual math that is in cookie clicker, its weird
    # do aging in here too, why not
    # and fungicide, live a little
    plotEffects = [1] * 36
    global plotAging
    global plotFungus
    plotAging = [1] * 36
    plotFungus = [1] * 36
    mult = SOILEFFECTS[soil.get()]
    for i in range(36):
        plant = gardenTiles[i].get()
        boost = 1
        aging = 1
        fungus = 1
        radius = 1
        applyEffect = False
        applyAging = False
        applyFungus = False
        if plant == "Лимон":
            boost = 0.8
            applyEffect = True
        elif plant == "Горох":
            boost = 1.2
            applyEffect = True
        elif plant == "Дыня":
            boost = 0.95
            applyEffect = True
        elif plant == "Черешня":
            boost = 0.5
            aging = 0.5
            applyEffect = True
            applyAging = True
        elif plant == "Картошка":
            aging = 1.03
            applyAging = True
        elif plant == "Слива":
            fungus = 0
            radius = 2
            applyFungus = True
        elif plant == "Клубника":
            fungus = 0
            applyFungus = True
        
        boost = NormalizeMult(boost, mult)
        aging = NormalizeMult(aging, mult)

        if applyEffect:
            plotEffects = AddBoost(i,1,boost,plotEffects)
        if applyAging:
            plotAging = AddBoost(i,1,aging, plotAging)
        if applyFungus:
            plotFungus = AddBoost(i, radius, fungus, plotFungus)
    return plotEffects

def EffectToString(effects, weights):
    tmpstr = ""
    for i in range(len(effects)):
        tmpstr += str(round(weights[i], 2))
        tmpstr += "% "
        tmpstr += EFFECTS[effects[i]]
        tmpstr += ", "
    return tmpstr

def RecalcEffects():
    tmpstr = ""
    effects = []
    weights = []
    global plotEffects
    plotEffects = RecalcPlotBoost()
    j = 0
    for plant in gardenTiles:
        idx = PLANTS.index(plant.get())
        numeffects = len(PLANTEFFECTS[idx][0])
        mult = SOILEFFECTS[soil.get()] * plotEffects[j]
        if numeffects > 0:
            for i in range(numeffects):
                if PLANTEFFECTS[idx][0][i] in effects:
                    fxidx = effects.index(PLANTEFFECTS[idx][0][i])
                    weights[fxidx] += PLANTEFFECTS[idx][1][i] * mult
                else:
                    effects.append(PLANTEFFECTS[idx][0][i])
                    weights.append(PLANTEFFECTS[idx][1][i] * mult)
        j += 1
    return EffectToString(effects, weights)

def MutationToString(muts, poss):
    retStr = ""
    for i in range(len(muts)):
        retStr += "\n"
        retStr += PLANTS[muts[i]] + " ("
        retStr += str(round(100 * poss[i], 2)) + "%)"
    return retStr

def AddMutation(muts, poss, plant, chance):
    if plant in muts:
        idx = muts.index(plant)
        poss[idx] += chance
    else:
        muts.append(plant)
        poss.append(chance)

def WoodchipRecalc(poss):
    # I don't know probability and statistics that well, hope this is close
    for i in range(2):
        total = 0
        for chance in poss:
            total += chance
        if total >= 1:
            return
        for j in range(len(poss)):
            poss[j] += (1 - total) * poss[j]

def GetMuts(i):
    possMuts = []
    mutChance = []
    
    if (gardenTiles[i].get() != "-"):
        if (gardenTiles[i].get() == "Картошка" or gardenTiles[i].get() == "Груша" or
            gardenTiles[i].get() == "Лимон" or gardenTiles[i].get() == "Арбуз" or
            gardenTiles[i].get() == "Дыня" or gardenTiles[i].get() == "Слива" or
            gardenTiles[i].get() == "Клубника" or plotFungus[i] != 1):
            return ""
            
        neighbors = {}
        x = i // 6
        y = i % 6
        for j in range(max(x - 1, 0), min(x + 2, 6)):
            for k in range(max(y - 1, 0), min(y + 2, 6)):
                if (j==x) != (k==y):
                    aPlant = gardenTiles[j * 6 + k].get()
                    if aPlant in neighbors:
                        neighbors[aPlant] += 1
                    else:
                        neighbors[aPlant] = 1
        if "Брокколи" in neighbors:
            possMuts.append("Брокколи")
            mutChance.append(0.05)
        if "Киви" in neighbors:
            possMuts.append("Киви")
            mutChance.append(0.03)
        if "Ананас" in neighbors:
            possMuts.append("Ананас")
            mutChance.append(0.03)
    else:
        neighbors = {}
        x = i // 6
        y = i % 6
        numNeighs = 0
        for j in range(max(x - 1, 0), min(x + 2, 6)):
            for k in range(max(y - 1, 0), min(y + 2, 6)):
                if j!=x or k!=y:
                    numNeighs += 1
                    aPlant = gardenTiles[j * 6 + k].get()
                    if aPlant in neighbors:
                        neighbors[aPlant] += 1
                    else:
                        neighbors[aPlant] = 1
        # because its easier than checking if it exists everytime
        for plant in PLANTS:
            if plant not in neighbors:
                neighbors[plant] = 0
        # whether fungus/weeds can grow, weed multipliers
        bFung = plotFungus[i] == 1
        wm = SOILWEEDS[soil.get()]
        cwm = min(wm, 1)
        # ALLLL the possibilities
        if neighbors["Лук"] >= 2:
            AddMutation(possMuts, mutChance, "Лук", 0.2)
            AddMutation(possMuts, mutChance, "Огурец", 0.05)
            AddMutation(possMuts, mutChance, "Перец", 0.001)
        if neighbors["Лук"] >= 1 and neighbors["Огурец"] >= 1:
            AddMutation(possMuts, mutChance, "Свекла", 0.01)
        if neighbors["Огурец"] >= 2:
            AddMutation(possMuts, mutChance, "Огурец", 0.1)
            AddMutation(possMuts, mutChance, "Лук", 0.05)
        if neighbors["Свекла"] >= 1 and neighbors["Огурец"] >= 1:
            AddMutation(possMuts, mutChance, "Чеснок", 0.03)
        if neighbors["Свекла"] >= 2:
            AddMutation(possMuts, mutChance, "Огурец", 0.02)
        if neighbors["Лук"] >= 1 and neighbors["Чеснок"] >= 1:
            AddMutation(possMuts, mutChance, "Помидор", 0.03)
            AddMutation(possMuts, mutChance, "Кукуруза", 0.0007)
        if neighbors["Помидор"] >= 1 and neighbors["Чеснок"] >= 1:
            AddMutation(possMuts, mutChance, "Дыня", 0.02)
        if neighbors["Помидор"] >= 2 and neighbors["Помидор"] < 5:
            AddMutation(possMuts, mutChance, "Помидор", 0.007)
            AddMutation(possMuts, mutChance, "Кукуруза", 0.0001)
        if neighbors["Помидор"] >= 4:
            AddMutation(possMuts, mutChance, "Кукуруза", 0.0007)
        if neighbors["Дыня"] >= 1 and neighbors["Свекла"] >= 1:
            AddMutation(possMuts, mutChance, "Картошка", 0.01)
        if neighbors["Банан"] >= 1 and neighbors["Свекла"] >= 1:
            AddMutation(possMuts, mutChance, "Картошка", 0.002)
        if neighbors["Лук"] >= 1 and neighbors["Виноград"] >= 1:
            AddMutation(possMuts, mutChance, "Свекла", 0.1)
        if neighbors["Морков"] >= 1 and neighbors["Апельсин"] >= 1:
            AddMutation(possMuts, mutChance, "Капуста", 0.1)
        if neighbors["Апельсин"] >= 1 and neighbors["Винроград"] <= 1 and bFung:
            AddMutation(possMuts, mutChance, "Виноград", 0.5)
        if neighbors["Виноград"] >= 1 and neighbors["Апельсин"] <= 1 and bFung:
            AddMutation(possMuts, mutChance, "Апельсин", 0.5)
        if neighbors["Брокколи"] >= 1 and neighbors["Брокколи"] <= 3 and bFung:
            AddMutation(possMuts, mutChance, "Брокколи", (0.15 * cwm))
        if neighbors["Дыня"] >= 1 and neighbors["Капуста"] >= 1:
            AddMutation(possMuts, mutChance, "Имбирь", 0.01)
        if neighbors["Дыня"] >= 1 and neighbors["Имбирь"] >= 1:
            AddMutation(possMuts, mutChance, "Редис", 0.05)
        if neighbors["Редис"] >= 2:
            AddMutation(possMuts, mutChance, "Редис", 0.005)
        if neighbors["Имбирь"] >= 2:
            AddMutation(possMuts, mutChance, "Горох", 0.05)
        if neighbors["Ананас"] >= 1 and neighbors["Яблоко"] >= 1:
            AddMutation(possMuts, mutChance, "Кабачок", 0.005)
        if ((neighbors["Ананас"] >= 1 and neighbors["Яблоко"] >= 1) or
            (neighbors["Ананас"] >= 1 and neighbors["Тыква"] >= 1)):
            AddMutation(possMuts, mutChance, "Тыква", 0.005)
        if neighbors["Тыква"] == 1:
            AddMutation(possMuts, mutChance, "Тыква", 0.05)
        if neighbors["Абрикос"] >= 1 and neighbors["Виноград"] >= 1:
            AddMutation(possMuts, mutChance, "Яблоко", 0.1)
        if neighbors["Яблоко"] == 1:
            AddMutation(possMuts, mutChance, "Яблоко", 0.05)
        if neighbors["Свекла"] >= 1 and neighbors["Перец"] >= 1:
            AddMutation(possMuts, mutChance, "Груша", 0.01)
        if neighbors["Груша"] >= 8:
            AddMutation(possMuts, mutChance, "Лимон", 0.001)
        if neighbors["Груша"] >= 2:
            AddMutation(possMuts, mutChance, "Арбуз", 0.001)
        if neighbors["Редис"] == 1 and bFung:
            AddMutation(possMuts, mutChance, "Ананас", 0.07)
        if neighbors["Редис"] >= 1 and neighbors["Огурец"] >= 1 and bFung:
            AddMutation(possMuts, mutChance, "Чеснок", 0.02)
        if neighbors["Редис"] >= 1 and neighbors["Баклажан"] >= 1 and bFung:
            AddMutation(possMuts, mutChance, "Гранат", 0.04)
        if neighbors["Киви"] >= 1 and neighbors["Кукуруза"] >= 1 and bFung:
            AddMutation(possMuts, mutChance, "Вишня", 0.04)
        if neighbors["Редис"] >= 2 and bFung:
            AddMutation(possMuts, mutChance, "Киви", 0.005)
        if neighbors["Киви"] == 1 and bFung:
            AddMutation(possMuts, mutChance, "Киви", 0.07)
        if neighbors["Киви"] >= 2 and bFung:
            AddMutation(possMuts, mutChance, "Редис", 0.005)
        if neighbors["Киви"] >= 1 and neighbors["Апельсин"] and bFung:
            AddMutation(possMuts, mutChance, "Банан", 0.06)
        if neighbors["Апельсин"] >= 1 and neighbors["Помидор"] >= 1 and bFung:
            AddMutation(possMuts, mutChance, "Кукуруза", 0.05)
        if neighbors["Банан"] >= 1 and neighbors["Картошка"] >= 1:
            AddMutation(possMuts, mutChance, "Дыня", 0.001)
        if neighbors["Картошка"] >= 5:
            AddMutation(possMuts, mutChance, "Дыня", 0.001)
        if neighbors["Арбуз"] >= 3:
            AddMutation(possMuts, mutChance, "Дыня", 0.005)
        if neighbors["Киви"] >= 4:
            AddMutation(possMuts, mutChance, "Дыня", 0.002)
        if neighbors["Груша"] >= 5:
            AddMutation(possMuts, mutChance, "Дыня", 0.001)
        if neighbors["Дыня"] == 1:
            AddMutation(possMuts, mutChance, "Дыня", 0.005)
        if neighbors["Лук"] >= 1 and neighbors["Капуста"] >= 1:
            AddMutation(possMuts, mutChance, "Слива", 0.002)
        if neighbors["Слива"] >= 3 and neighbors["Картошка"] >= 3:
            AddMutation(possMuts, mutChance, "Клубника", 0.002)
        if neighbors["Картошка"] >= 1 and neighbors["Редис"] >= 1 and bFung:
            AddMutation(possMuts, mutChance, "Черешня", 0.002)
        # apply woodchip effects to chances
        if soil.get() == 5:
            WoodchipRecalc(mutChance)

        
        if neighbors["-"] == numNeighs and bFung:
            AddMutation(possMuts, mutChance, "Med", (0.002 * wm))
    return MutationToString(possMuts, mutChance)

def GetNewInfo(i):
    global plotEffects
    global plotAging
    global plotFungus
    retStr = "Посаженно: "
    retStr += PLANTS[gardenTiles[i].get()]
    idx = PLANTS.index(gardenTiles[i].get())
    if len(PLANTEFFECTS[idx][0]) > 0:
        retStr += "\nЭффекты: "
        retStr += EffectToString(PLANTEFFECTS[idx][0], PLANTEFFECTS[idx][1])
    mult = SOILEFFECTS[soil.get()] * plotEffects[i]
    if plotEffects[i] != 1:
        retStr += "\nМножитель Эффекта: "
        retStr += str(round(plotEffects[i], 2))
    if plotAging[i] != 1:
        retStr += "\nМножитель старение : "
        retStr += str(round(plotAging[i], 2))
    if plotFungus[i] != 1:
        retStr += "\nСредство от сорняков/грибков: 100%"
    mutStr = GetMuts(i)
    if mutStr != "":
        retStr += "\nВозможные эффекты:" + mutStr
    return retStr


"""
***********************************
STEP 2: BUILD 
***********************************
"""
# Main garden tiles
gardenBtns = []
gardenTtps = []
for i in range(36):
    wid = OptionMenu(root,gardenTiles[i],
                   *PLANTS)
    wid.grid(row=(i % 6),column=(i // 6))
    gardenBtns.append(wid)
    t = createToolTip(wid, "Посажено : Ничего")
    gardenTtps.append(t)

# These functions need to be below the tooltips but above buttons
def UpdateToolTips():
    for i in range(36):
        gardenTtps[i].settext(GetNewInfo(i))

def FillAll(event=None):
    tofill = gardenFill.get()
    for plant in gardenTiles:
        plant.set(tofill)
    return

def RefreshWindow(event=None):
    gardenStatus.config(state=NORMAL)
    gardenStatus.delete(1.0, END)
    gardenStatus.insert(END, RecalcEffects())
    gardenStatus.config(state=DISABLED)
    UpdateToolTips()
    return

# Soil selector
i = 0
for txt, val in SOILS:
    if i < 4:
        Radiobutton(root, text=txt, variable=soil, value=val).grid(
            row=6, column=i)
    else:
        Radiobutton(root, text=txt, variable=soil, value=val).grid(
            row=6, column=i, columnspan=2)
    i+=1

# Info box
gardenStatus = Text(root, height=4, width=58, relief=SUNKEN)
gardenStatus.grid(row=7,column=0,columnspan=6,rowspan=4)
gardenStatus.insert(END, "Эффекты сада появятся здесь после запуска процесса!")
gardenStatus.config(state=DISABLED)


# Extra buttons
Button(root, text="Запуск процесса",
               command=RefreshWindow).grid(row=11,column=0,columnspan=2)
Button(root, text="Заполнить все",
       command=FillAll).grid(row=11,column=3)
Label(root,text="c:").grid(row=11,column=4)
OptionMenu(root,gardenFill,*PLANTS).grid(row=11,column=5)

root.mainloop()
