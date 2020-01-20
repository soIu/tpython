##  C version of the systems programming language benchmark
##  Author:  M. J. Jordan  Cambridge Computer Laboratory.
##
##  Modified by:  M. Richards, Nov 1996
##    to be ANSI C and runnable on 64 bit machines + other minor changes
##  Modified by:  M. Richards, 20 Oct 1998
##    made minor corrections to improve ANSI compliance (suggested
##    by David Levine)
##  Modified by:  DJ Raptor, Jan 20th, 2020
##    ported to Pythonic++
##

with c++:
	Count=10000
	Qpktcountval=23246
	Holdcountval=9297
	TRUE  = 1
	FALSE = 0
	MAXINT = 32767
	BUFSIZE       = 3
	I_IDLE        = 1
	I_WORK        = 2
	I_HANDLERA    = 3
	I_HANDLERB    = 4
	I_DEVA        = 5
	I_DEVB        = 6
	PKTBIT        = 1
	WAITBIT       = 2
	HOLDBIT       = 4
	S_RUN         = 0
	S_RUNPKT      = 1
	S_WAIT        = 2
	S_WAITPKT     = 3
	S_HOLD        = 4
	S_HOLDPKT     = 5
	S_HOLDWAIT    = 6
	S_HOLDWAITPKT = 7
	K_DEV  = 1000
	K_WORK = 1001
	define(NOTPKTBIT  = !1)
	define(NOTWAITBIT = !2)
	define(NOTHOLDBIT = 0XFFFB)
	class packet:
		packet  *p_link
		int      p_id
		int      p_kind
		int      p_a1
		char     p_a2[BUFSIZE+1];
	class task:
		task    *t_link
		int      t_id
		int      t_pri
		packet  *t_wkq
		int      t_state
		task    *(*t_fn)(packet *);
		long     t_v1
		long     t_v2
	alphabet[28] = "0ABCDEFGHIJKLMNOPQRSTUVWXYZ";
	task *tasktab[11] =  {(task *)10,0,0,0,0,0,0,0,0,0,0};
	task *tasklist    =  0;
	task *tcb;
	taskid = 0
	v1 = 0
	v2 = 0
	qpktcount =  0
	holdcount =  0
	tracing   =  0
	layout    =  0
	def append(pkt, ptr):
		pkt->p_link = 0
		while ( ptr->p_link ) ptr = ptr->p_link
		ptr->p_link = pkt
	## everybody hates C style function pointers - goodbye C/C++ style, hello auto templates ##
	##def createtask(int id, int pri, packet *wkq, int state, task *(*fn)(packet *), long v1, long v2):
	def createtask(id, pri, wkq, state, fn, v1, v2):
		task *t = (task *)malloc(sizeof(task))
		tasktab[id] = t
		t->t_link   = tasklist
		t->t_id     = id
		t->t_pri    = pri
		t->t_wkq    = wkq
		t->t_state  = state
		t->t_fn     = fn
		t->t_v1     = v1
		t->t_v2     = v2
		tasklist    = t
	## note: can not use auto templates everywhere, the compiler must be able to deduce the types,
	## here link must be typed as `packet*`
	def pkt(packet *link, id, kind) -> packet*:
		int i
		packet *p = (packet *)malloc(sizeof(packet))
		for (i=0; i<=BUFSIZE; i++):
			p->p_a2[i] = 0
		p->p_link = link
		p->p_id = id
		p->p_kind = kind
		p->p_a1 = 0
		return p
	def trace(a):
		if ( --layout <= 0 ):
			printf("\n")
			layout = 50
		printf("%c", a)
	def schedule():
		while tcb != 0:
			packet *pkt
			task *newtcb
			pkt=0
			switch (tcb->t_state):
				case S_WAITPKT:
					pkt = tcb->t_wkq;
					tcb->t_wkq = pkt->p_link;
					tcb->t_state = tcb->t_wkq == 0 ? S_RUN : S_RUNPKT;
				case S_RUN:
					pass
				case S_RUNPKT:
					taskid = tcb->t_id;
					v1 = tcb->t_v1;
					v2 = tcb->t_v2;
					if (tracing):
						trace(taskid+'0');
					newtcb = (*(tcb->t_fn))(pkt);
					tcb->t_v1 = v1;
					tcb->t_v2 = v2;
					tcb = newtcb;
					break;
				case S_WAIT:
					pass
				case S_HOLD:
					pass
				case S_HOLDPKT:
					pass
				case S_HOLDWAIT:
					pass
				case S_HOLDWAITPKT:
					tcb = tcb->t_link;
					break;
				default:
					return;
	def wait_task() ->task*:
		tcb->t_state |= WAITBIT;
		return (tcb);
	def holdself() ->task*:
		++holdcount
		tcb->t_state |= HOLDBIT
		return (tcb->t_link)
	def findtcb(id) ->task*:
		task *t = 0
		if (1<=id && id<=(long)tasktab[0]) t = tasktab[id];
		if (t==0) printf("\nBad task id %d\n", id);
		return t
	def release(id) ->task*:
		task *t;
		t = findtcb(id)
		if ( t==0 ) return (0);
		t->t_state &= NOTHOLDBIT;
		if ( t->t_pri > tcb->t_pri ) return (t);
		return tcb
	def qpkt(pkt) -> task*:
		task *t
		t = findtcb(pkt->p_id)
		if (t==0) return (t);
		qpktcount++
		pkt->p_link = 0
		pkt->p_id = taskid
		if t->t_wkq==0:
			t->t_wkq = pkt
			t->t_state |= PKTBIT
			if (t->t_pri > tcb->t_pri) return (t);
		else:
			append(pkt, (packet *)&(t->t_wkq))
		return tcb
	def idlefn(packet *pkt) -> task*:
		if --v2==0:
			return holdself()
		if (v1&1) == 0:
			v1 = ( v1>>1) & MAXINT
			return release(I_DEVA)
		else:
			v1 = ( (v1>>1) & MAXINT) ^ 0XD008
			return release(I_DEVB)
	def workfn(packet *pkt) -> task*:
		if pkt==0:
			return wait_task()
		else:
			int i;
			v1 = I_HANDLERA + I_HANDLERB - v1;
			pkt->p_id = v1;
			pkt->p_a1 = 0;
			for (i=0; i<=BUFSIZE; i++):
				v2++
				if ( v2 > 26 ) v2 = 1; (pkt->p_a2)[i] = alphabet[v2];
			return qpkt(pkt)
	def handlerfn(packet *pkt) -> task*:
		if pkt != 0:
			append(pkt, (packet *)(pkt->p_kind==K_WORK ? &v1 : &v2))
		if v1 != 0:
			int count
			packet *workpkt = (packet *)v1
			count = workpkt->p_a1
			if count > BUFSIZE:
				v1 = (long)(((packet *)v1)->p_link)
				return qpkt(workpkt)
			if v2 != 0:
				packet *devpkt
				devpkt = (packet *)v2
				v2 = (long)(((packet *)v2)->p_link)
				devpkt->p_a1 = workpkt->p_a2[count];
				workpkt->p_a1 = count+1
				return qpkt(devpkt)
		return wait_task()
	def devfn(packet *pkt) -> task*:
		if pkt == 0:
			if v1 == 0:
				return wait_task()
			pkt = (packet *)v1
			v1 = 0;
			return qpkt(pkt)
		else:
			v1 = (long)pkt
			if (tracing) trace(pkt->p_a1);
			return holdself()
	def bench() ->int:
		packet *wkq = 0
		createtask(I_IDLE, 0, wkq, S_RUN, idlefn, 1, Count)
		wkq = pkt(0, 0, K_WORK)
		wkq = pkt(wkq, 0, K_WORK)
		createtask(I_WORK, 1000, wkq, S_WAITPKT, workfn, I_HANDLERA, 0)
		wkq = pkt(0, I_DEVA, K_DEV)
		wkq = pkt(wkq, I_DEVA, K_DEV)
		wkq = pkt(wkq, I_DEVA, K_DEV)
		createtask(I_HANDLERA, 2000, wkq, S_WAITPKT, handlerfn, 0, 0)
		wkq = pkt(0, I_DEVB, K_DEV)
		wkq = pkt(wkq, I_DEVB, K_DEV)
		wkq = pkt(wkq, I_DEVB, K_DEV)
		createtask(I_HANDLERB, 3000, wkq, S_WAITPKT, handlerfn, 0, 0)
		wkq = 0
		createtask(I_DEVA, 4000, wkq, S_WAIT, devfn, 0, 0)
		createtask(I_DEVB, 5000, wkq, S_WAIT, devfn, 0, 0)
		tcb = tasklist
		qpktcount = holdcount = 0
		tracing = FALSE
		layout = 0
		schedule()
		if not (qpktcount == Qpktcountval && holdcount == Holdcountval):
			printf("qpkt count = %d  holdcount = %d\n", qpktcount, holdcount)
			printf("These results are incorrect")
			exit(1)
		return qpktcount
	@module( my_cpp_module )
	def run_richards_bench(loops):
		print("enter richards...")
		int total = 0
		for i in range( int(loops) ):
			total += bench()
		print(total)
		return None


import my_cpp_module

def main():
	print('enter main...')
	LOOPS = 24
	my_cpp_module.run_richards_bench( LOOPS )

main()
