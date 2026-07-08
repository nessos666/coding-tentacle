"""
GEHIRN BF — Braitenberg Vehicles Brain
EINFACHSTE SENSOREN → KOMPLEXES VERHALTEN.
14 Fahrzeugtypen: von Angst (Typ 2) bis Optimismus (Typ 14).
Jeder Bug aktiviert Sensor-Motor-Verschaltung.

Mathematik: Motor_L = f(Sensor_L, Sensor_R)  (direkt/schlicht)
           Motor_R = f(Sensor_R, Sensor_L)  (gekreuzt/komplex)

Autor: Hermes + David | Coding Tentacle 2026
Quelle: Braitenberg "Vehicles: Experiments in Synthetic Psychology" (1984)
"""
import numpy as np, math
from collections import defaultdict

class BraitenbergBrain:
    """Gehirn BF — Einfachste Sensoren, emergentes Verhalten (Braitenberg)."""
    def __init__(self):
        # 5 Fahrzeug-Typen als Fix-Strategien
        self.vehicles={
            'type2_fear': {'sensor':'bug_severity','motor':'escape','cross':True},   # Angst
            'type4_aggression': {'sensor':'fix_success','motor':'attack','cross':True},  # Aggression
            'type6_love': {'sensor':'pattern_familiarity','motor':'approach','cross':False}, # Liebe
            'type10_curiosity': {'sensor':'bug_novelty','motor':'explore','cross':True}, # Neugier
            'type14_optimism': {'sensor':'all_positive','motor':'apply','cross':False}  # Optimismus
        }
        self.sensors={'bug_severity':0,'fix_success':0,'pattern_familiarity':0,'bug_novelty':0,'all_positive':0}
        self.patterns=defaultdict(lambda: {'success':0,'total':0})
        self.total_bugs=0
    
    def _update_sensors(self, emb, success):
        """Sensor-Werte aus Embedding und Erfolg ableiten"""
        e=np.array(emb)
        self.sensors['bug_severity']=float(np.std(e[:64]) if len(e)>=64 else 0.5)
        self.sensors['fix_success']=1.0 if success else 0.0
        self.sensors['pattern_familiarity']=float(np.mean(e[:32]) if len(e)>=32 else 0.5)
        self.sensors['bug_novelty']=1.0/(1.0+self.total_bugs*0.01)
        self.sensors['all_positive']=max(0, np.mean(list(self.sensors.values())[:4]))
    
    def _motor_output(self, vehicle, crossed):
        """Direkte vs gekreuzte Verschaltung"""
        if vehicle=='type2_fear':
            sensor_val=self.sensors['bug_severity']
            if crossed:
                return ('EXPLORE', 1.0-sensor_val)  # Angst → weglaufen = explore
            return ('APPLY_PATTERN', sensor_val)
        elif vehicle=='type4_aggression':
            if crossed:
                return ('APPLY_PATTERN', self.sensors['fix_success'])
            return ('EXPLORE', 1.0-self.sensors['fix_success'])
        elif vehicle=='type6_love':
            if crossed:
                return ('EXPLORE', 1.0-self.sensors['pattern_familiarity'])
            return ('APPLY_PATTERN', self.sensors['pattern_familiarity'])
        elif vehicle=='type10_curiosity':
            if crossed:
                return ('EXPLORE', self.sensors['bug_novelty'])
            return ('APPLY_PATTERN', 1.0-self.sensors['bug_novelty'])
        elif vehicle=='type14_optimism':
            return ('APPLY_PATTERN', self.sensors['all_positive'])
        return ('EXPLORE', 0.0)
    
    def think(self,sig,emb):
        self.total_bugs+=1; bt=sig.split(':')[0] if ':' in sig else sig
        self._update_sensors(emb, self.patterns[bt]['success']/max(1,self.patterns[bt]['total'])>0.5 if self.patterns[bt]['total']>0 else False)
        
        # Alle Fahrzeuge "fahren" — wähle bestes
        best_vehicle,best_action,best_conf=None,'EXPLORE',0
        for vname,vdata in self.vehicles.items():
            action,conf=self._motor_output(vname, vdata['cross'])
            if conf>best_conf: best_conf=conf; best_action=action; best_vehicle=vname
        
        return {'action':best_action,'pattern':f'vehicle_{bt}','confidence':best_conf,
                'active_vehicle':best_vehicle,
                'reasoning':f'Braitenberg: Vehicle={best_vehicle} → {best_action} (conf={best_conf:.2f})'}
    
    def learn(self,sig,pat,success,emb=None):
        bt=sig.split(':')[0] if ':' in sig else sig
        self.patterns[bt]['total']+=1
        if success: self.patterns[bt]['success']+=1
    
    def stats(self):
        return {'brain_type':'Braitenberg Vehicles','total_bugs':self.total_bugs,
                'vehicles':len(self.vehicles),
                'sensors':{k:f'{v:.2f}' for k,v in self.sensors.items()}}
    def __repr__(self): return f"BraitenbergBrain(vehicles={len(self.vehicles)})"

if __name__=="__main__":
    print("GEHIRN BF — Braitenberg Vehicles"); b=BraitenbergBrain()
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer('all-MiniLM-L6-v2')
    for i in range(20):
        bt=['NullPointer','OffByOne','TypeError'][i%3]
        emb=m.encode(f"{bt} error").tolist()
        dec=b.think(f"{bt}:f{i}.py:{i}",emb)
        b.learn(f"{bt}:f{i}.py:{i}",f"fix_{bt}",i<16,emb)
        if i%4==0: print(f"  Bug{i+1}: {dec['action']:15s} vehicle={dec.get('active_vehicle','?')}")
    print(b.stats()); print("✅ Gehirn BF läuft.")
