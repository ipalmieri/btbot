from abc import ABCMeta, abstractmethod
from sqlalchemy.orm.session import make_transient
import btools, dbcon, settings

logger = btools.logger


class baseCrud:
    """ Base class for CRUD operations and persistence
    """
    __metaclass__ = ABCMeta    
    
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def reload(self, obj):
        pass

    @abstractmethod
    def save(self, obj):
        pass

    @abstractmethod
    def delete(self, obj):
        pass

    
    
class dbCrud(baseCrud):
    """ CRUD operations using database
    """
    
    def __init__(self):
        self.dbsession = dbcon.session()

        
    def __del__(self):
        self.dbsession.close()

        
    def add(self, obj):
        self.dbsession.add(obj)
        ret = dbcon.safe_commit(self.dbsession)
        self.dbsession.refresh(obj)
        make_transient(obj)
        return ret

    
    def reload(self, obj):
        try:
            obj = self.dbsession.merge(obj)
            self.dbsession.refresh(obj)
        except Exception, e:
            logger.error("Error reloading object")
        else:
            make_transient(obj)
        return obj

    
    def save(self, obj):
        self.dbsession.add(obj)
        ret = dbcon.safe_commit(self.dbsession)
        make_transient(obj)
        return ret

    
    def delete(self, obj):
        obj = self.dbsession.merge(obj)
        self.dbsession.delete(obj)
        ret = dbcon.safe_commit(self.dbsession)
        make_transient(obj)
        return ret

    

class baseAR():

    def add(self):
        pobj = dbCrud()
        return pobj.add(self)

    def reload(self):
        pobj = dbCrud()
        return pobj.reload(self)

    def save(self):
        pobj = dbCrud()
        return pobj.save(self)

    def delete(self):
        pobj = dbCrud()
        return pobj.delete(self)

