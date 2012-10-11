# Copyright (c) 2008, Johan Lindberg [johan@pulp.se]
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the <ORGANIZATION> nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys

#import clips
from myclips import Network as MyClipsEngine
from myclips.shell.Interpreter import Interpreter as MyClipsInterpreter

import wx
import wx.xrc

class SudokuDemo(wx.App):
    def OnInit(self):
        # Load the Sudoku solving programs
        #clips.Load("sudoku.clp")
        #clips.Load("solve.clp")
        
        self.engine = MyClipsEngine()
        self.interpreter = MyClipsInterpreter(self.engine)
        
        self.interpreter.evaluate('(load "../res/sudoku/sudoku.clp")')
        self.interpreter.evaluate('(load "../res/sudoku/solve.clp")')
        self.interpreter.evaluate('(load "../res/sudoku/output-frills.clp")')
        self.interpreter.evaluate('(watch rules)')
        
        
        # Load the GUI from SudokuDemo.xrc
        resource = wx.xrc.XmlResource('SudokuDemo.xrc')
        self.frame = resource.LoadFrame(None, 'SudokuDemoFrame')
        
        # Store references to widgets that are being used at run-time.
        self.openfile = wx.xrc.XRCCTRL(self.frame, 'OpenFile')
        self.clear = wx.xrc.XRCCTRL(self.frame, 'Clear')
        self.reset = wx.xrc.XRCCTRL(self.frame, 'Reset')
        self.solve = wx.xrc.XRCCTRL(self.frame, 'Solve')
        self.techniques = wx.xrc.XRCCTRL(self.frame, 'Techniques')
        
        # Bind button events to handler functions
        self.openfile.Bind(wx.EVT_BUTTON, self.on_openfile)
        self.clear.Bind(wx.EVT_BUTTON, self.on_clear)
        self.reset.Bind(wx.EVT_BUTTON, self.on_reset)
        self.solve.Bind(wx.EVT_BUTTON, self.on_solve)
        self.techniques.Bind(wx.EVT_BUTTON, self.on_techniques)
        
        # Set max length in each of the wx.TextCtrls to 1. This can,
        # sadly, NOT be done using XRCEd.
        for g in range(1,10):
            for c in range(1,10):
                cell = wx.xrc.XRCCTRL(self.frame, '%d%d' % (g, c))
                cell.SetMaxLength(1)
                
        self.solved = False
        self.resetvalues = {}
        
        # Bind the close event to the exit function and show the GUI
        self.frame.Bind(wx.EVT_CLOSE, self.exit)
        self.frame.Show(True)
        
        return True
        
    def on_openfile(self, event):
        """
        Loads a Sudoku puzzle from disk.
        """
        
        # Show a File Open Dialog
        dlg = wx.FileDialog(self.frame,
                            message = "Open a Sudoku puzzle",
                            style = wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.solved = False
            
            self.solve.Enable(True)
            self.techniques.Enable(False)
            
            path = dlg.GetPath()
            
            puzzle = open(path)
            positions = {   1 : [11, 12, 13, 21, 22, 23, 31, 32, 33],
                            2 : [14, 15, 16, 24, 25, 26, 34, 35, 36],
                            3 : [17, 18, 19, 27, 28, 29, 37, 38, 39],
                            
                            4 : [41, 42, 43, 51, 52, 53, 61, 62, 63],
                            5 : [44, 45, 46, 54, 55, 56, 64, 65, 66],
                            6 : [47, 48, 49, 57, 58, 59, 67, 68, 69],
                            
                            7 : [71, 72, 73, 81, 82, 83, 91, 92, 93],
                            8 : [74, 75, 76, 84, 85, 86, 94, 95, 96],
                            9 : [77, 78, 79, 87, 88, 89, 97, 98, 99]    }
                            
            lines = 0
            for line in puzzle.readlines():
                lines += 1
                line = line.strip()
                if len(line) != 9:
                    raise Exception("Malformed puzzle!")
                    
                cells = positions[lines]
                for id, value in zip(cells, line):
                    cell = wx.xrc.XRCCTRL(self.frame, '%d' % (id))
                    if value in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                        cell.SetValue(str(value))
                    else:
                        cell.SetValue("")
                    cell.SetSize((20,20))
                    
            if lines != 9:
                raise Exception("Malformed puzzle!")
                
            puzzle.close()
            
    def on_clear(self, event):
        """
        Clears the Sudoku grid.
        """
        
        self.solved = False
        
        self.solve.Enable(True)
        self.techniques.Enable(False)
        
        for g in range(1,10):
            for c in range(1,10):
                cell = wx.xrc.XRCCTRL(self.frame, '%d%d' % (g, c))
                cell.SetValue("")
                cell.SetSize((20,20))
                
    def on_reset(self, event):
        """
        Resets the Sudoku grid to the last puzzle solved.
        """
        
        self.solved = False
        
        self.solve.Enable(True)
        self.techniques.Enable(False)
        
        for g in range(1,10):
            for r in range(3):
                for c in range(3):
                    cell = wx.xrc.XRCCTRL(self.frame, '%d%d' % (g, (r* 3)+ c+ 1))
                    try:
                        cell.SetValue(self.resetvalues[(g,r,c)])
                    except:
                        cell.SetValue("")
                    cell.SetSize((20,20))
                    
    def on_solve(self, event):
        """
        Solves the Sudoku puzzle and updates the grid with the solution.
        """
        
        #clips.Reset()
        #clips.Assert("(phase expand-any)")
        #clips.Assert("(size 3)")
        self.engine.reset()
        self.interpreter.evaluate('(assert (phase expand-any))')
        self.interpreter.evaluate('(assert (size 3))')
        
        # Remember the initial starting values
        # of the puzzle for the reset command.
        
        self.resetvalues = {}
        
        for i in range(9):
            rowgroup = i / 3
            colgroup = i % 3
            for r in range(3):
                for c in range(3):
                    cell = wx.xrc.XRCCTRL(self.frame, '%d%d' % (i+ 1, (r* 3)+ c+ 1))
                    self.resetvalues[(i+ 1,r,c)] = cell.GetValue()
                    
                    assertStr = "(possible (row %d) (column %d) (group %d) (id %d) " % \
                                ((r + (rowgroup * 3) + 1),
                                 (c + (colgroup * 3) + 1),
                                 (i + 1), ((i * 9) + (r * 3) + c + 1))
                                 
                    if self.resetvalues[(i+ 1,r,c)] == "":
                        assertStr = assertStr + "(value any))"
                    else:
                        assertStr = assertStr + "(value " + self.resetvalues[(i+ 1, r, c)] + "))"
                        
                    #clips.Assert(str(assertStr))
                    self.interpreter.evaluate('(assert %s)'%str(assertStr))
                    
        self.solved = True
        self.reset.Enable(True)
        self.solve.Enable(False)
        self.techniques.Enable(True)
        
        # Solve the puzzle
        #clips.Run()
        self.engine.run()
        
        ff = self.engine.facts
        for f in ff:
            print f
        
        # Retrieve the solution from CLIPS.
#        for i in range(9):
#            rowgroup = i / 3
#            colgroup = i % 3
#            for r in range(3):
#                for c in range(3):
#                    cell = wx.xrc.XRCCTRL(self.frame, '%d%d' % (i+ 1, (r* 3)+ c+ 1))
#                    if cell.GetValue() == "":
#                        # Any cells that have not been assigned a value
#                        # are given a '?' for their content
#                        cell.SetValue("?")
#                        
#                        evalStr = "(find-all-facts ((?f possible)) (and (eq ?f:row %d) (eq ?f:column %d)))" % \
#                                  ((r + (rowgroup * 3) + 1),
#                                   (c + (colgroup * 3) + 1))
#                                   
#                        pv = clips.Eval(evalStr)
#                        if len(pv) == 1:
#                            fv = pv[0]
#                            cell.SetValue(str(fv.Slots["value"]))
                            
                            
    def on_techniques(self, event):
        """
        Opens a wx.Dialog that displays which solution techniques was
        used to solve the current puzzle.
        """
        
#        evalStr = "(find-all-facts ((?f technique)) TRUE)";
#        techniques = clips.Eval(evalStr)
#        
#        message = ""
#        tNum = len(techniques)
#        for i in range(1, tNum+ 1):
#            evalStr = "(find-fact ((?f technique-employed)) (eq ?f:priority %d))" % (i)
#            pv = clips.Eval(evalStr)
#            
#            if len(pv) > 0:
#                fv = pv[0]
#                
#                message = "%s\n%s. %s" % (message, fv.Slots["priority"], fv.Slots["reason"])

        message = "Bho"
                
        dlg = wx.MessageDialog(self.frame, message, "Solution Techniques",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def exit(self, event):
        """
        Destroys the GUI and exits the application.
        """
        
        self.frame.Destroy()
        sys.exit(0)
        
if __name__ == '__main__':
    app= SudokuDemo(0)
    app.MainLoop()
