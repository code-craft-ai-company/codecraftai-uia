
from typing import List, Optional, Tuple

import os

from datetime import datetime, timedelta

import AppKit

from mojo.errors.exceptions import SemanticError

from mojo.uia.wrappers.uiametadataitem import UiaMetadataItem

EMPTY_TUPLE = tuple()

class SearchPredicate:

    def __init__(self, query: str, args: Optional[List[str]] = EMPTY_TUPLE):
        self._query = query
        self._args = args
        return
    
    @property
    def args(self) -> Tuple[str]:
        return tuple(self._args)

    @property
    def query(self) -> str:
        return self._query


class UiaMetadataQuery:

    def __init__(self, predicate: SearchPredicate, timeout: int = 20, interval: float = .5):
        self._timeout = timeout
        self._interval = interval

        self._finished = False
        self._results = None
        
        self._mdquery = AppKit.NSMetadataQuery.alloc().init()

        self._ncenter = AppKit.NSNotificationCenter.defaultCenter()        
        self._ncenter.addObserver_selector_name_object_(
            self, "_queryNotification:", None, self._mdquery
        )

        self._predicate = AppKit.NSPredicate.predicateWithFormat_(predicate.query, *predicate.args)
        self._mdquery.setPredicate_(self._predicate)

        return
    
    @property
    def results(self) -> List[UiaMetadataItem]:
        return self._results

    def run(self) -> List[UiaMetadataItem]:

        if self._finished:
            errmsg = "UiaMetadataQuery.run called on previously run query.  Each query can only be used once."
            raise SemanticError(errmsg)

        self._mdquery.startQuery()

        now_time = datetime.now()
        start_time = now_time
        end_time = start_time + timedelta(seconds=self._timeout)

        while not self._finished:

            now_time = datetime.now()

            if now_time > end_time:
                errmsg_lines = [
                    f"Timeout error running query. start={start_time} end={end_time} now={now_time}"
                ]
                errmsg = os.linesep.join(errmsg_lines)
                raise TimeoutError(errmsg)
            
            AppKit.NSRunLoop.currentRunLoop().runUntilDate_(
                now_time + timedelta(seconds=self._interval)
            )

        return self._results

    def _queryNotification_(self, notification):

        notification_name = notification.name()
        if notification_name == AppKit.NSMetadataQueryDidFinishGatheringNotification:
            self._mdquery.stopQuery()
            self._results = [UiaMetadataItem(rv) for rv in notification.object().results()]
            self._finished = True

        return