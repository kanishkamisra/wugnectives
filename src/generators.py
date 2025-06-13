from dataclasses import dataclass


@dataclass
class Inference:
    inference: str

    def generate(self, entity, prefix) -> str:
        return f"{prefix} {entity} {self.inference}".strip()


@dataclass
class DualEntityInference:
    inference: str

    def generate(self, e1, e2, prefix) -> str:
        return f"{prefix} {e1} {self.inference} {e2}".strip()


@dataclass
class Premise:
    e1: str
    e2: str
    premise: str

    def __post_init__(self):
        self.premise = self.premise.replace("[e1]", self.e1).replace("[e2]", self.e2)


@dataclass
class PreferencePremise(Premise):
    pref_verb: str
    prop: str
    prop_phrase: str

    def __post_init__(self):
        super().__post_init__()
        self.inf = Inference(self.prop_phrase)
        self.premise = (
            self.premise.replace("[pref-verb]", self.pref_verb)
            .replace("[property]", self.prop)
            .strip()
        )

    def generate_inference_pair(self, prefix="This means that") -> str:
        inference1 = self.inf.generate(self.e1, prefix)
        inference2 = self.inf.generate(self.e2, prefix)
        return self.premise, inference1, inference2


@dataclass
class TemporalPremise(Premise):
    order: str

    def __post_init__(self):
        super().__post_init__()
        self.inf = DualEntityInference(f"started {self.order}")

    def generate_inference_pair(self, prefix="This means that") -> str:
        inference1 = self.inf.generate(self.e1, self.e2, prefix)
        inference2 = self.inf.generate(self.e2, self.e1, prefix)
        return self.premise, inference1, inference2


@dataclass
class CausalPremise(Premise):

    def __post_init__(self):
        super().__post_init__()
        self.inf = DualEntityInference(f"causes")

    def generate_inference_pair(self, prefix="This means that") -> str:
        inference1 = self.inf.generate(self.e1, self.e2, prefix)
        inference2 = self.inf.generate(self.e2, self.e1, prefix)
        return self.premise, inference1, inference2
    
@dataclass
class AsGoalPremise(Premise):

    def __post_init__(self):
        super().__post_init__()
        self.inf = DualEntityInference(f"requires")

    def generate_inference_pair(self, prefix="This means that") -> str:
        inference1 = self.inf.generate(self.e1, self.e2, prefix)
        inference2 = self.inf.generate(self.e2, self.e1, prefix)
        return self.premise, inference1, inference2
    
@dataclass
class InstantiationPremise(Premise):
    
        def __post_init__(self):
            super().__post_init__()
            self.inf = DualEntityInference(f"are")
    
        def generate_inference_pair(self, prefix="This means that") -> str:
            inference1 = self.inf.generate(self.e1, self.e2, prefix)
            inference2 = self.inf.generate(self.e2, self.e1, prefix)
            return self.premise, inference1, inference2
