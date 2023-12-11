from __future__ import generators
import plus
import AI
from AI import vector3
import Arenas
import Gooey
import math
import JTactics
import Tactics


class JAI(AI.SuperAI):
    "Currently a clone of Pusher for testing"
    name = "JAI"

    def __init__(self, **args):
        AI.SuperAI.__init__(self, **args)

        #self.tactics.append(JTactics.Push(self))
        self.tactics.append(JTactics.JCharge(self))
        #self.tactics.append(Tactics.Shove(self))
        #self.tactics.append(Tactics.Charge(self))

    def Activate(self, active):
        if active:
            if AI.SuperAI.debugging:
                self.debug = Gooey.Plain("watch", 0, 75, 100, 75)
                tbox = self.debug.addText("line0", 0, 0, 100, 15)
                tbox.setText("Throttle")
                tbox = self.debug.addText("line1", 0, 15, 100, 15)
                tbox.setText("Turning")
                tbox = self.debug.addText("line2", 0, 30, 100, 15)
                tbox.setText("")
                tbox = self.debug.addText("line3", 0, 45, 100, 15)
                tbox.setText("")

        return AI.SuperAI.Activate(self, active)

    def LostComponent(self, id):
        # print "Lost Component!"
        return AI.SuperAI.LostComponent(self, id)

    def DebugString(self, id, string):
        if self.debug:
            if id == 0:
                self.debug.get("line0").setText(string)
            elif id == 1:
                self.debug.get("line1").setText(string)
            elif id == 2:
                self.debug.get("line2").setText(string)
            elif id == 3:
                self.debug.get("line3").setText(string)


AI.register(JAI)
