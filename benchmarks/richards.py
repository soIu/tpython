# based on a Java version:
#  Based on original version written in BCPL by Dr Martin Richards
#  in 1981 at Cambridge University Computer Laboratory, England
#  and a C++ version derived from a Smalltalk version written by
#  L Peter Deutsch.
#  Java version:  Copyright (C) 1995 Sun Microsystems, Inc.
#  Translation from C++, Mario Wolczko
#  Outer loop added by Alex Jacoby

# Task IDs
I_IDLE = 1
I_WORK = 2
I_HANDLERA = 3
I_HANDLERB = 4
I_DEVA = 5
I_DEVB = 6
# Packet types
K_DEV = 1000
K_WORK = 1001
# Packet
BUFSIZE = 4
TASKTABSIZE = 10
tracing = False
layout = 0

def trace(a):
	global layout
	layout -= 1
	if layout <= 0:
		print()
		layout = 50
	print(a)

class Packet(object):
	def __init__(self,l,i,k):
		self.link = l
		self.ident = i
		self.kind = k
		self.datum = 0
		self.data = [0] * BUFSIZE

	def append_to(self,lst):
		self.link = None
		if lst is None:
			return self
		else:
			p = lst
			next = p.link
			while next is not None:
				p = next
				next = p.link
			p.link = self
			return lst

# Task Records
class TaskRec(object):
	pass
class DeviceTaskRec(TaskRec):
	def __init__(self):
		self.pending = None
class IdleTaskRec(TaskRec):
	def __init__(self):
		self.control = 1
		self.count = 10000
class HandlerTaskRec(TaskRec):
	def __init__(self):
		self.work_in = None
		self.device_in = None
	def workInAdd(self,p):
		self.work_in = p.append_to(self.work_in)
		return self.work_in
	def devInAdd(self,p):
		self.device_in = p.append_to(self.device_in)
		return self.device_in

class WorkerTaskRec(TaskRec):
	def __init__(self):
		self.dest = I_HANDLERA
		self.count = 0
# Task
class TaskState(object):
	def __init__(self):
		self.pktpending = True
		self.tskwaiting = False
		self.tskholding = False
	def packetPending(self):
		self.pktpending = True
		self.tskwaiting = False
		self.tskholding = False
		return self
	def waiting(self):
		self.pktpending = False
		self.tskwaiting = True
		self.tskholding = False
		return self
	def running(self):
		self.pktpending = False
		self.tskwaiting = False
		self.tskholding = False
		return self
	# waiting with packet
	def waitPacket(self):
		self.pktpending = True
		self.tskwaiting = True
		self.tskholding = False
		return self
	# is packet pending
	def isPending(self):
		return self.pktpending
	# is task waiting
	def isTskWait(self):
		return self.tskwaiting
	# is task holding
	def isTskHold(self):
		return self.tskholding
	# task holding or waiting
	def isHoldWait(self):
		return self.tskholding or (not self.pktpending and self.tskwaiting)
	# is waiting with packet
	def isWaitPkt(self):
		return self.pktpending and self.tskwaiting and not self.tskholding

class TaskWorkArea(object):
	def __init__(self):
		self.taskTab = [None] * TASKTABSIZE
		self.taskList = None
		self.holdCount = 0
		self.qpktCount = 0

WorkArea = TaskWorkArea()

class Task(TaskState):
	def __init__(self,i,p,w,initialState,r):
		self.link = WorkArea.taskList
		self.ident = i
		self.priority = p
		self.input = w
		self.pktpending = initialState.isPending()
		self.tskwaiting = initialState.isTskWait()
		self.tskholding = initialState.isTskHold()
		self.handle = r
		WorkArea.taskList = self
		WorkArea.taskTab[i] = self

	def fn(self,pkt,r):
		raise NotImplementedError

	def addPacket(self,p,old):
		if self.input is None:
			self.input = p
			self.pktpending = True
			if self.priority > old.priority:
				return self
		else:
			p.append_to(self.input)
		return old

	def runTask(self):  ## most CPU load
		if self.isWaitPkt():
			msg = self.input
			self.input = msg.link
			if self.input is None:
				self.running()
			else:
				self.packetPending()
		else:
			msg = None
		return self.fn(msg,self.handle)

	def waitTask(self):
		self.tskwaiting = True
		return self

	def hold(self):
		WorkArea.holdCount += 1
		self.tskholding = True
		return self.link

	def findtcb(self,id):
		t = WorkArea.taskTab[id]
		if t is None:
			print('Exception in findtcb')
		return t

	def release(self,i):
		t = self.findtcb(i)
		t.tskholding = False
		if t.priority > self.priority:
			return t
		else:
			return self
	def qpkt(self,pkt):
		t = self.findtcb(pkt.ident)
		WorkArea.qpktCount += 1
		pkt.link = None
		pkt.ident = self.ident
		p = t.addPacket(pkt,self)
		return p

			
# DeviceTask

class DeviceTask(Task):
	def __init__(self,i,p,w,s,r):
		Task.__init__(self,i,p,w,s,r)

	def fn(self,pkt,r):
		d = r
		if pkt is None:
			pkt = d.pending
			if pkt is None:
				tsk = self.waitTask()
				return tsk
			else:
				d.pending = None
				return self.qpkt(pkt)
		else:
			d.pending = pkt
			if tracing: trace(pkt.datum)
			return self.hold()

class HandlerTask(Task):
	def __init__(self,i,p,w,s,r):
		Task.__init__(self,i,p,w,s,r)

	def fn(self,pkt,r):
		h = r
		if pkt is not None:
			if pkt.kind == K_WORK:
				h.workInAdd(pkt)
			else:
				h.devInAdd(pkt)
		work = h.work_in
		if work is None:
			tsk = self.waitTask()
			return tsk
		count = work.datum
		if count >= BUFSIZE:
			h.work_in = work.link
			return self.qpkt(work)

		dev = h.device_in
		if dev is None:
			tsk = self.waitTask()
			return tsk

		h.device_in = dev.link
		dev.datum = work.data[count]
		work.datum = count + 1
		return self.qpkt(dev)

# IdleTask

class IdleTask(Task):
	def __init__(self,i,p,w,s,r):
		Task.__init__(self,i,0,None,s,r)

	def fn(self,pkt,r):
		i = r
		i.count -= 1
		if i.count == 0:
			return self.hold()
		elif (i.control & 1) == 0:
			i.control = int(i.control / 2)
			t = self.release(I_DEVA)
			return t
		else:
			i.control = int(i.control/2) ^ 0xd008
			t = self.release(I_DEVB)
			return t

# WorkTask

A = ord('A')

class WorkTask(Task):
	def __init__(self,i,p,w,s,r):
		Task.__init__(self,i,p,w,s,r)

	def fn(self,pkt,r):
		w = r
		if pkt is None:
			tsk = self.waitTask()
			return tsk
		if w.dest == I_HANDLERA:
			dest = I_HANDLERB
		else:
			dest = I_HANDLERA
		w.dest = dest
		pkt.ident = dest
		pkt.datum = 0
		for i in range(BUFSIZE):
			w.count += 1
			if w.count > 26:
				w.count = 1
			pkt.data[i] = A + w.count - 1
		return self.qpkt(pkt)

def schedule():
	t = WorkArea.taskList
	while t is not None:
		pkt = None
		if tracing:
			print("tcb =",t.ident)
		if t.isHoldWait():
			t = t.link
		else:
			if tracing: trace(chr(ord("0")+t.ident))
			t = t.runTask()

class Richards(object):
	def run(self, iterations):
		for i in range(iterations):
			WorkArea.holdCount = 0
			WorkArea.qpktCount = 0
			ts1 = TaskState()
			IdleTask(I_IDLE, 1, 10000, ts1.running(), IdleTaskRec())
			wkq = Packet(None, 0, K_WORK)
			wkq = Packet(wkq , 0, K_WORK)
			ts2 = TaskState()
			WorkTask(I_WORK, 1000, wkq, ts2.waitPacket(), WorkerTaskRec())

			wkq = Packet(None, I_DEVA, K_DEV)
			wkq = Packet(wkq , I_DEVA, K_DEV)
			wkq = Packet(wkq , I_DEVA, K_DEV)
			ts3 = TaskState()
			HandlerTask(I_HANDLERA, 2000, wkq, ts3.waitPacket(), HandlerTaskRec())

			wkq = Packet(None, I_DEVB, K_DEV)
			wkq = Packet(wkq , I_DEVB, K_DEV)
			wkq = Packet(wkq , I_DEVB, K_DEV)
			ts4 = TaskState()
			HandlerTask(I_HANDLERB, 3000, wkq, ts4.waitPacket(), HandlerTaskRec())

			wkq = None;
			ts5 = TaskState()
			DeviceTask(I_DEVA, 4000, wkq, ts5.waiting(), DeviceTaskRec());
			ts6 = TaskState()
			DeviceTask(I_DEVB, 5000, wkq, ts6.waiting(), DeviceTaskRec());
			
			schedule()
			
			if WorkArea.holdCount == 9297 and WorkArea.qpktCount == 23246:
				pass
			else:
				print(WorkArea.holdCount)				
				print(WorkArea.qpktCount)
				return False

		return True

def entry_point(iterations):
	r = Richards()
	result = r.run(iterations)
	if not result:
		print('#ERROR incorrect results!')

def main():
	iterations = 24
	total_s = entry_point(iterations)

main()
