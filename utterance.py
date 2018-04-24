import re
from spans import intrange
from konlpy.tag import Twitter


class Utterance:

    __slot_pattern = re.compile(r'\(([^)]+)\)\[([^\]]+)\]')
    __tokenizer = Twitter()

    def __init__(self, utterance: str, tokens: list, labels: list):
        if len(utterance) == 0:
            raise ValueError('utterance should not be empty.')

        if len(tokens) != len(labels):
            raise ValueError('tokens and labels should have same length.')

        self.__utterance = utterance
        self.__tokens = tokens
        self.__labels = labels

    @classmethod
    def parse(cls, utterance: str):
        entities = []
        while True:
            m = cls.__slot_pattern.search(utterance)
            if not m:
                break
            text = m.group(1)
            label = m.group(2)
            start = m.start()
            end = start + len(text)
            entities.append({
                'text': text,
                'label': label,
                'span': intrange(start, end)
            })
            utterance = utterance.replace(m.group(0), text, 1)

        idx = 0
        tokens = []
        labels = []
        for token in cls.__tokenizer.morphs(utterance):
            start = utterance.index(token, idx)
            end = start + len(token)
            span = intrange(start, end)
            tokens.append(token)
            idx = end

            found = False
            for entity in entities:
                if entity['span'].contains(span):
                    label = ('b-' if entity['span'].lower == span.lower else 'i-') + entity['label']
                    labels.append(label)
                    found = True
                    break
            if not found:
                labels.append('o')

        return Utterance(utterance, tokens, labels)

    def __str__(self):
        return str({
            'utterance': self.__utterance,
            'tokens': self.__tokens,
            'labels': self.__labels
        })
