

from music21 import *
import numpy as np
import random

class JazzAutomataCompositore:
    def __init__(self, width=8, generations=16):
        self.width = width
        self.generations = generations
        
        # Stati possibili per ogni cella
        # 0: Silenzio
        # 1: Nota fondamentale
        # 2: Terza
        # 3: Settima
        # 4: Tensione (note di passaggio/alterazioni)
        # 5: Risposta melodica
        self.num_states = 6
        
        # Scale jazz comuni per ogni grado della progressione
        self.scales = {
            'ii': scale.DorianScale('D'),
            'V': scale.MixolydianScale('G'),
            'I': scale.MajorScale('C')
        }
        
        # Progressione di base ii-V-I
        self.progression = ['ii', 'V', 'I', 'I']
        self.current_chord_idx = 0
        
    def _get_chord_tones(self, chord_type):
        """Ottiene le note principali per il tipo di accordo corrente"""
        if chord_type == 'ii':
            return ['D', 'F', 'A', 'C']
        elif chord_type == 'V':
            return ['G', 'B', 'D', 'F']
        else:  # I
            return ['C', 'E', 'G', 'B']
    
    def _inizializza_griglia(self):
        """Inizializza la griglia con alcuni musicisti attivi"""
        # Assicuriamo che ci sia almeno un musicista che suona la fondamentale
        grid = np.zeros(self.width, dtype=int)
        grid[random.randint(0, self.width-1)] = 1
        
        # Aggiungi altri musicisti 
        for i in range(self.width):
            if grid[i] == 0 and random.random() < 0.4:
                grid[i] = random.randint(1, self.num_states-1)
        return grid
    
    def _risposta_jazz(self, stato_corrente, stati_vicini, chord_type):
        """Determina come un musicista risponde basandosi sui vicini e l'armonia"""
        
        # Conta quanti vicini stanno suonando
        vicini_attivi = sum(1 for s in stati_vicini if s > 0)
        
        # Se nessuno sta suonando nelle vicinanze
        if vicini_attivi == 0:
            return random.randint(1, 3) if random.random() < 0.3 else 0
            
        # Se il musicista sta già suonando
        if stato_corrente > 0:
            if 5 in stati_vicini:
                return 5  
            elif random.random() < 0.4:
                #la probabilità di passare a una tensione riflette l'idea queste sono frequenti nel jazz.
                return 4  
            else:
              #questa invece è per aumentare la possibilità che il musicista resti dentro l'armonia
                return random.randint(1, 3)  
                
        # Se ci sono molti musicisti attivi, maggiore probabilità di pause, per rendere più dinamica la melodia
        if vicini_attivi > 2 and random.random() < 0.6:
            return 0
            
        # Rispondi alle frasi melodiche dei vicini
        if 4 in stati_vicini or 5 in stati_vicini:
            # Se ci sono tensioni o melodie nei vicini, aumentà la possibilità 
            return 5 if random.random() < 0.7 else 4
            
        return random.randint(1, 3)
    
    def _evolvi_generazione(self, generazione):
        """Evolve una generazione di musicisti jazz"""
        nuova_gen = np.zeros(self.width, dtype=int)
        chord_type = self.progression[self.current_chord_idx]
        
        for i in range(self.width):
            # Prendi gli stati dei musicisti vicini
            vicini = [
                generazione[(i - 2) % self.width],
                generazione[(i - 1) % self.width],
                generazione[(i + 1) % self.width],
                generazione[(i + 2) % self.width]
            ]
            
            nuova_gen[i] = self._risposta_jazz(generazione[i], vicini, chord_type)
        
        # Avanza nella progressione armonica
        self.current_chord_idx = (self.current_chord_idx + 1) % len(self.progression)
        return nuova_gen
    
    def _stato_a_nota(self, stato, chord_type):
        """Converte uno stato in una nota musicale basata sull'armonia corrente"""
        if stato == 0:
            return None
            
        chord_tones = self._get_chord_tones(chord_type)
        scale = self.scales[chord_type]
        
        if stato in [1, 2, 3]:  # Note dell'accordo
            return note.Note(chord_tones[stato-1], quarterLength=1)
        elif stato == 4:  # Note di tensione
            tensions = [p for p in scale.getPitches() if str(p) not in chord_tones]
            return note.Note(random.choice(tensions), quarterLength=0.5)
        else:  # Risposta melodica
            all_notes = scale.getPitches()
            return note.Note(random.choice(all_notes), quarterLength=random.choice([0.25, 0.5]))
    
    def genera_composizione(self):
        """Genera una composizione jazz completa"""
        score = stream.Score()
        part = stream.Part()
        
        # Configurazione iniziale
        part.append(meter.TimeSignature('4/4'))
        part.append(key.Key('C'))
        
        # Genera e converti l'evoluzione dell'automa in musica
        grid = self._inizializza_griglia()
        measure = stream.Measure()
        current_time = 0
        
        for gen in range(self.generations):
            chord_type = self.progression[self.current_chord_idx]
            
            # Converti gli stati in note
            for stato in grid:
                nota = self._stato_a_nota(stato, chord_type)
                if nota:
                    if current_time + nota.quarterLength > 4.0:
                        part.append(measure)
                        measure = stream.Measure()
                        current_time = 0
                    measure.append(nota)
                    current_time += nota.quarterLength
            
            # Evolvi alla prossima generazione
            grid = self._evolvi_generazione(grid)
        
        # Aggiungi l'ultima battuta se non vuota
        if len(measure) > 0:
            part.append(measure)
        
        score.append(part)
        return score

def main():
    compositore = JazzAutomataCompositore()
    score = compositore.genera_composizione()
    score.write('musicxml', 'jazz_improvisation.musicxml')
    print("Composizione jazz generata con successo!")

if __name__ == "__main__":
    main()
