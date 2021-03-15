from threading import Thread
from time import sleep, time
from progress.bar import Bar


def thread(target, args, cooldown, message):
  threads = []
  for arg in args:
    t = Thread(target=target, args=arg)
    threads.append(t)
  bar = Bar(message if message else 'Processing', max=len(threads))
  for i, t in enumerate(threads):
    t.start()
    bar.next()
    sleep(cooldown)

  for t in threads:
    t.join()
  bar.finish()


def threads(target, args, cooldown=0, message=None):
  start = time()

  thread(target, args, cooldown, message)

  end = time()
  hours, rem = divmod(end-start, 3600)
  minutes, seconds = divmod(rem, 60)
  print("Took {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
