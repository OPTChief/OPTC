from orator import DatabaseManager, Model

# Configuration de la base de données sakura.db 
sakura = {'mysql': {'driver': 'sqlite', 'database': './sakura.db'}}

# connexion à la base de données sakura.db
db_glb = DatabaseManager(sakura)

# Définition de la classe "quest" pour utiliser les données de la table "MstQuest_"
class quest(Model):
    __table__ = 'MstQuest_'

class characters(Model):
    __table__ = 'MstCharacter_'

class eventsRelation(Model):
    __table__ = 'MstEventQuestRelation_'
        
class events(Model):
    __table__ = 'MstEvent_'
    
class events_schedule(Model):
    __table__ = 'MstEventSchedule_'
    
class gashas_free_schedule(Model):
    __table__ = 'MstFreeGashaSchedule_'
class gashas(Model):
    __table__ = 'MstGasha_'
class dbversion(Model):
    __table__ = 'dbversion'
class colosseum_group_boss(Model):
    __table__ = 'MstColosseumGroupBoss_'

class ship_level(Model):
    __table__ = 'MstShipLevel_'
    
class ship_name(Model):
    __table__ = 'MstShip_'
    
class grand_voyage(Model):
    __table__ = 'MstVoyageQuestMissionLevel_'
class trials_quests(Model):
    __table__ = 'MstTrailGridQuest_'