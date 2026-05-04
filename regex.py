from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    next_states: list[State]
    @abstractmethod
    def __init__(self) -> None:
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    def __init__(self):
        super().__init__()
    def check_self(self, char):
        return False

class TerminationState(State):
    def __init__(self):
        super().__init__()
    def check_self(self, char: str):
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """
    def __init__(self):
        super().__init__()
    def check_self(self, char: str):
        return len(char) == 1


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    curr_sym = ""
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol
    def check_self(self, char: str) -> bool:
        return char == self.curr_sym


class StarState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.repeating = checking_state
    def check_self(self, char):
        if self.repeating.check_self(char):
            return True
        return False


class PlusState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.plus_state = checking_state
    def check_self(self, char):
        return self.plus_state.check_self(char)


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state: State = StartState()
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            new_s = self.__init_next_state(char, prev_state, tmp_next_state)
            if char not in "*+":
                prev_state.next_states.append(new_s)
                prev_state = new_s
                tmp_next_state = new_s

        prev_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None
        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                # new_state = tmp_next_state
                # tmp_next_state.next_states.append(new_state)
                # new_state.next_states.append(new_state)
                tmp_next_state.next_states.append(tmp_next_state)
                return tmp_next_state
            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                tmp_next_state.next_states.append(new_state)
                new_state.next_states.append(new_state)
            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)
            case _:
                raise AttributeError("Character is not supported")
        return new_state

    def check_string(self, user_inut):
        def check(state: State, text: str, visited = None) -> bool:
            if visited is None:
                visited = set()

            state_id = (id(state), len(text))
            if state_id in visited:
                return False
            visited.add(state_id)
            if not text:
                if isinstance(state, TerminationState):
                    return True
                for n_state in state.next_states:
                    if check(n_state, "", visited):
                        return True
                return False


            for next_s in state.next_states:
                if check(next_s, text, visited):
                    return True
            if text:
                for next_s in state.next_states:
                    if next_s.check_self(text[0]):
                        if check(next_s, text[1:], None):
                            return True
            return False
        return check(self.curr_state, user_inut)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)
    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
    new_tests = [
    ("a*4.+hi", "4!hi", True),      # a*(0) + 4 + .+(!) + hi
    ("a*4.+hi", "aaa4   hi", True),  # a*(3) + 4 + .+(пробіл) + hi
    ("a*4.+hi", "a4ABCDEhi", True),  # a*(1) + 4 + .+(ABCDE) + hi

    ("b*3.+ok", "3!ok", True),       # b*(0) + 3 + .+(!) + ok
    ("b*3.+ok", "bb3XYZok", True),   # b*(2) + 3 + .+(XYZ) + ok

    ("x*.y+z", "xyzz", True),        # x*(1) + .(y) + z(2)
    ("x*.y+z", "xxxy+zz", True),     # x*(3) + .(y) + +(+) + z(2)

    ("m+n.*p", "mmn123p", True),     # m(1) + n(1) + .*(123) + p
    ("m+n.*p", "mXYZp", True),       # m(1) + n(0 via *) + .*(XYZ) + p

    ("k*5.+zz", "5Azz", True),       # k*(0) + 5 + .+(A) + zz
    ("k*5.+zz", "kkk5!@#zz", True),  # k*(3) + 5 + .+(!@#) + zz

    ("c+7.*end", "c7end", True),     # c(1) + 7 + .*(порожньо) + end
    ("c+7.*end", "cc7Xend", True),   # c(2) + 7 + .*(X) + end
]
    for pattern, text, expected in new_tests:
        fsm = RegexFSM(pattern)
        result = fsm.check_string(text)
        print(f"✅ NEW: {pattern=} {text=} → {result}")
