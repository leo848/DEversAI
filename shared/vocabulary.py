import base64
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Iterable

@dataclass
class MergeRule:
    left: 'Token'
    right: 'Token'
    result: 'Token'

class Node:
    def __init__(self, value: int, next: Optional['Node'] = None):
        self.value = value
        self.next = next


class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None
        self.size: int = 0

    @classmethod
    def from_iterable(cls, iterable: Iterable[int]) -> 'LinkedList':
        ll = cls()
        nodes = []
        for item in iterable:
            nodes.append(Node(item))
        if nodes:
            ll.head = nodes[0]
            current = ll.head
            for node in nodes[1:]:
                assert current is not None
                current.next = node
                current = node
            ll.size = len(nodes)
        return ll

    def to_array(self) -> List[int]:
        arr = []
        current = self.head
        while current:
            arr.append(current.value)
            current = current.next
        return arr


class Token:
    def __init__(self, index: int, value: bytes, vocab: Optional['Vocabulary'] = None):
        self.index = index
        self.value = value
        self.vocab = vocab
        self.composition: Optional[tuple[Token, Token]] = None
        self.children: tuple[list[Token], list[Token]] = ([], [])

        try:
            self.display_string = value.decode('utf-8')
        except UnicodeDecodeError:
            self.display_string = f'<{self.index}>'

        if vocab is not None:
            assert len(vocab.tokens) == index
            vocab.tokens.append(self)
            vocab.display_set[self.display_string] = self

    def id(self) -> int:
        return self.index

    def __str__(self) -> str:
        return self.display_string

    def __repr__(self) -> str:
        return f'Token({self.index}, {self.value})'

    def history_tree(self) -> dict:
        assert self.vocab is not None, 'No vocabulary for token'
        if self.composition is None:
            return {'name': self.display_string, 'id': self.index}
        else:
            return {
                'name': self.display_string.replace(' ', '⎵').replace('\n', '\\n'),
                'id': self.index,
                'children': [
                    self.composition[0].history_tree(),
                    self.composition[1].history_tree()
                ]
            }

    def is_byte(self) -> bool:
        return self.index < 256


class Vocabulary:
    def __init__(self, merge_rules: List[Tuple[int, int]]):
        self.tokens: List[Token] = []
        self.merge_rules: List[MergeRule] = []
        self.display_set: Dict[str, Token] = {}

        while len(self.tokens) < 256:
            self.mint_byte_token()

        for left_idx, right_idx in merge_rules:
            if left_idx >= len(self.tokens) or right_idx >= len(self.tokens):
                raise AssertionError('Merge rule on unknown token')
            left = self.tokens[left_idx]
            right = self.tokens[right_idx]
            if left is None or right is None:
                raise AssertionError('Merge rule on unknown token')
            token = self.mint_merged_token(left, right)
            token.composition = (left, right)
            left.children[0].append(token)
            right.children[1].append(token)
            self.merge_rules.append(MergeRule(left=left, right=right, result=token))

    @classmethod
    def from_base64(cls, base64_str: str) -> 'Vocabulary':
        decoded_bytes = base64.b64decode(base64_str)
        if len(decoded_bytes) % 2 != 0:
            raise ValueError('Base64 data length must be even')
        uint16_list = []
        for i in range(0, len(decoded_bytes), 2):
            hi = decoded_bytes[i]
            lo = decoded_bytes[i + 1]
            uint16 = (hi << 8) | lo
            uint16_list.append(uint16)
        merge_rules = []
        for i in range(0, len(uint16_list), 2):
            if i + 1 >= len(uint16_list):
                break
            merge_rules.append((uint16_list[i], uint16_list[i + 1]))
        return cls(merge_rules)

    @classmethod
    def from_vocab_file(cls, content: str) -> 'Vocabulary':
        lines = content.strip().split('\n')
        merge_rules = []
        current_id = 256
        for line in lines:
            if not line.strip():
                continue
            parts = list(map(int, line.split()))
            if len(parts) != 3:
                raise ValueError(f'Invalid line: {line}')
            left, right, rule_id = parts
            if rule_id != current_id:
                raise AssertionError(f'Expected id {current_id}, got {rule_id}')
            merge_rules.append((left, right))
            current_id += 1
        return cls(merge_rules)

    def mint_byte_token(self) -> Token:
        index = len(self.tokens)
        value = bytes([index])
        return Token(index, value, self)

    def mint_merged_token(self, left: Token, right: Token) -> Token:
        index = len(self.tokens)
        merged_value = left.value + right.value
        return Token(index, merged_value, self)

    def tokenize(self, input_str: str, last_applied_merge_rule: Optional[int] = None) -> List[Token]:
        inf = len(self.tokens) * 2
        if last_applied_merge_rule is None:
            last_applied_merge_rule = +inf

        bytes_input = input_str.encode('utf-8')
        token_list = LinkedList.from_iterable(bytes_input)
        reverse_merge_rules = {
            (rule.left.id(), rule.right.id()): rule.result.id() for rule in self.merge_rules
        }

        while True:
            min_rule_id = +inf
            current = token_list.head
            while current and current.next:
                key = (current.value, current.next.value)
                result_id = reverse_merge_rules.get(key, +inf)
                if result_id < min_rule_id:
                    min_rule_id = result_id
                current = current.next

            if min_rule_id == +inf or min_rule_id > last_applied_merge_rule:
                break

            rule = self.merge_rules[min_rule_id - 256]
            left_id = rule.left.id()
            right_id = rule.right.id()
            result_id = rule.result.id()

            current = token_list.head
            while current and current.next:
                if current.value == left_id and current.next.value == right_id:
                    current.value = result_id
                    current.next = current.next.next
                    token_list.size -= 1
                else:
                    current = current.next

        token_ids = token_list.to_array()
        return [
            self.tokens[id_]
            for id_ in token_ids
            if id_ < +inf
        ]
