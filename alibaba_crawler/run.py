# coding: utf8 
import time
import threading
from search_seller_worker import SearchSellerWorker
from update_seller_worker import UpdateSellerWorker
from scan_seller_worker import ScanSellerWorker
from update_item_worker import UpdateItemWorker


def main(args=None):
    workers = []
    workers += [SearchSellerWorker(i) for i in range(1)]
    workers += [UpdateSellerWorker(i) for i in range(1)]
    workers += [ScanSellerWorker(i) for i in range(2)]
    workers += [UpdateItemWorker(i) for i in range(2)]

    for w in workers:
        w.daemon = True
        w.start()

    while threading.active_count() > 1:
        time.sleep(0.2)


if __name__ == '__main__':
    main()
