# MIT License
#
# Copyright (c) 2022 Eric Thiffeault
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://github.com/ethiffeault/etsm

class State:
    def __init__(self, enter, exit):
        self.Enter = enter
        self.Exit = exit

class StateMachine:
    def __init__(self, owner):
        self.Owner = owner
        self.Current = None
        self.__inTransition = False

    def Transition(self, state) -> bool :
        if ( self.__inTransition):
            return False;

        self.__inTransition = True

        if (self.Current != None and self.Current.Exit != None):
            self.Current.Exit(self.Owner)

        self.Current = state

        if (self.Current != None and self.Current.Enter != None):
            self.Current.Enter(self.Owner)

        self.__inTransition = False
        return True

    def IsIn(self, state):
        return self.Current == state