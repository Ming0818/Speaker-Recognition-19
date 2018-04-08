import pyaudio
import numpy as np
import pylab
import time

RATE = 44410
CHUNK = int(RATE/20)

def plot(stream):
    t1=time.time()
    data = np.frombuffer(stream.read(CHUNK),dtype=np.int16);
    pylab.plot(data)
    pylab.title("Plotting")
    pylab.grid()
    pylab.axes([0,len(data),2**16,2**16/2])
    pylab.savefig("03.jpg",dpi=50)
    pylab.close("all")
    print("took %.2f ms"%(time.time()-t1)*1000)

if __name__ == "__main__":
    p=pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,frames_per_buffer=CHUNK)
    for i in range(int(20*RATE/CHUNK)):
        plot(stream)
    stream.stop_stream()
    stream.close()
    p.terminate()


