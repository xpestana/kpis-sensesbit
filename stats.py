from abc import ABC, abstractmethod
from uuid import UUID

import numpy as np
import statsmodels.api as sm
import statsmodels.stats.multitest as smm
from models import AnswerBase, Attribute, CodeSample, Question, Sample, Translation
from scipy import stats as scipy_stats
from scipy.special import gammaincc
from statsmodels.formula.api import ols


def get_translation(item, key, selected_lang):
    item_translations = [
        translation for translation in item.translations if translation.key == key
    ]
    item_translation = Translation.get_preferred_lang(item_translations, selected_lang)
    return item_translation


class AggregatedSession(AnswerBase):
    sections: list["AggregatedSection"]

    def __init__(self):
        self.sections = []


class AggregatedSection(AnswerBase):
    id: int
    repeated_by_sample: bool
    order: int
    questions: list["AggregatedQuestion"]

    def __init__(self, section):
        self.id = section.id
        self.repeated_by_sample = section.repeated_by_sample
        self.order = section.order
        self.questions = []


class AggregatedQuestion(AnswerBase):
    id: int
    type: int
    order: int
    multiple: bool
    triangle: bool
    discrete: bool
    required: bool
    name: str
    lang: str
    stats: list["Stats"]
    results: list["AggregatedAnswer"]
    samples: list["AggregatedSample"]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, question, selected_lang):
        self.id = question.id
        self.type = question.type
        self.order = question.order
        self.multiple = question.multiple
        self.triangle = question.triangle
        self.discrete = question.discrete
        self.required = question.required
        translation: Translation = get_translation(
            question, key="name", selected_lang=selected_lang
        )
        self.name = translation.value
        self.lang = translation.lang
        self.stats = []
        self.results = []
        self.samples = []


class AggregatedSample(AnswerBase):
    code_sample_id: int
    sample_id: int
    code_sample_code: str
    code_sample_lang: str
    sample_name: str
    results: list["AggregatedAnswer"]

    def __init__(self, code_sample, selected_lang):
        self.code_sample_id = code_sample.id
        self.sample_id = code_sample.sample_id
        translation: Translation = get_translation(
            code_sample, key="code", selected_lang=selected_lang
        )
        self.code_sample_code = translation.value
        self.code_sample_lang = translation.lang
        sample: Sample = code_sample.sample
        self.sample_name = sample.name
        self.results = []


class DataCleaner(ABC):
    @abstractmethod
    def execute(self, CleanData, answers, selected_lang) -> pd.DataFrame:
        pass


class CleanerType1(DataCleaner):
    def execute(self, CleanData, answers, selected_lang) -> pd.DataFrame:
        data = []
        for answer in answers:
            placeholder = answer.placeholder
            name = get_translation(
                placeholder, key="name", selected_lang=selected_lang
            ).value
            data.append(
                {
                    "user_id": answer.user_id,
                    "placeholder_id": answer.placeholder_id,
                    "placeholder_order": placeholder.order,
                    "placeholder_name": name,
                    "code_sample_id": answer.code_sample_id,
                }
            )
        clean_df = pd.DataFrame(
            data,
            columns=[
                "user_id",
                "placeholder_id",
                "placeholder_order",
                "placeholder_name",
                "code_sample_id",
            ],
        )
        return clean_df


class CleanerType2(DataCleaner):
    def execute(self, CleanData, answers, selected_lang=None) -> pd.DataFrame:
        data = []
        for answer in answers:
            data.append(
                {
                    "user_id": answer.user_id,
                    "value": answer.value,
                    "code_sample_id": answer.code_sample_id,
                }
            )
        clean_df = pd.DataFrame(data, columns=["user_id", "value", "code_sample_id"])
        return clean_df


class CleanerType3Attributes(DataCleaner):
    def execute(self, CleanData, answers, selected_lang=None) -> pd.DataFrame:
        data = []
        for answer in answers:
            if answer.value:
                data.append(
                    {
                        "user_id": answer.user_id,
                        "attribute_id": answer.attribute_id,
                        "code_sample_id": answer.code_sample_id,
                    }
                )
        clean_df = pd.DataFrame(
            data, columns=["user_id", "attribute_id", "code_sample_id"]
        )
        return clean_df


class CleanerType3Samples(DataCleaner):
    def execute(self, CleanData, answers, selected_lang=None) -> pd.DataFrame:
        data = []
        for answer in answers:
            if answer.value:
                data.append(
                    {"user_id": answer.user_id, "code_sample_id": answer.code_sample_id}
                )
        clean_df = pd.DataFrame(data, columns=["user_id", "code_sample_id"])
        return clean_df


class CleanerType4(DataCleaner):
    def execute(self, CleanData, answers, selected_lang=None) -> pd.DataFrame:
        data = []
        for answer in answers:
            data.append(
                {
                    "user_id": answer.user_id,
                    "code_sample_id": answer.code_sample_id,
                    "order": answer.value,
                }
            )
        clean_df = pd.DataFrame(data, columns=["user_id", "code_sample_id", "order"])
        return clean_df


class CleanData:
    question: Question
    attribute_id: int | None
    clean_data: pd.DataFrame | None
    data_cleaner: DataCleaner | None

    def __init__(self, question, attribute_id=None, data_cleaner=None):
        self.attribute_id = attribute_id
        self.question = question
        if data_cleaner:
            self.set_data_cleaner(data_cleaner)
        else:
            selected_data_cleaner = self.select_data_cleaner(question)
            self.set_data_cleaner(selected_data_cleaner)

    def select_data_cleaner(self, question):
        if question.type == 1:
            return CleanerType1()
        elif question.type == 2:
            return CleanerType2()
        elif question.type == 3:
            if len(question.attributes) != 0:
                return CleanerType3Attributes()
            else:
                return CleanerType3Samples()
        elif question.type == 4:
            return CleanerType4()

    def set_data_cleaner(self, data_cleaner):
        self.data_cleaner = data_cleaner

    def execute_cleaner(self, answers, selected_lang):
        if self.data_cleaner is None:
            raise ValueError("data_cleaner not set")
        else:
            return self.data_cleaner.execute(self, answers, selected_lang)


class Aggregator(ABC):
    @abstractmethod
    def execute(
        self,
        aggregated_answer,
        clean_data: pd.DataFrame,
        selected_lang: str,
        attribute: Attribute | None = None,
        code_sample: CodeSample | None = None,
    ):
        pass


class AggregatorType1(Aggregator):
    def execute(
        self,
        aggregated_answer,
        clean_data: pd.DataFrame,
        selected_lang: str,
        attribute: Attribute | None = None,
        code_sample: CodeSample | None = None,
    ):
        aggregated_answer.mean_order = float(clean_data["placeholder_order"].mean())
        try:
            aggregated_answer.mean_value = float(
                clean_data["placeholder_name"].astype(float).mean()
            )
        except ValueError:
            aggregated_answer.mean_value = None
        for placeholder in attribute.placeholders:
            aggregated_placeholder = AggregatedPlaceholder(
                placeholder,
                selected_lang,
                "name",
                clean_data,
            )
            aggregated_answer.placeholders.append(aggregated_placeholder)
        pass


class AggregatorType2(Aggregator):
    def execute(
        self,
        aggregated_answer,
        clean_data: pd.DataFrame,
        selected_lang: str,
        attribute: Attribute | None = None,
        code_sample: CodeSample | None = None,
    ):
        aggregated_answer.text = clean_data["value"].iloc[0]
        aggregated_answer.user_id = clean_data["user_id"].iloc[0]
        pass


class AggregatorType3Attributes(Aggregator):
    def execute(
        self,
        aggregated_answer,
        clean_data: pd.DataFrame,
        selected_lang: str,
        attribute: Attribute | None = None,
        code_sample: CodeSample | None = None,
    ):
        n_responses = clean_data["user_id"].nunique()
        filtered_clean_data = clean_data[clean_data["attribute_id"] == attribute.id]
        aggregated_answer.n = len(filtered_clean_data)
        aggregated_answer.percent = (len(filtered_clean_data) / n_responses) * 100
        pass


class AggregatorType3Samples(Aggregator):
    def execute(
        self,
        aggregated_answer,
        clean_data: pd.DataFrame,
        selected_lang: str,
        attribute: Attribute | None = None,
        code_sample: CodeSample | None = None,
    ):
        n_responses = clean_data["user_id"].nunique()
        filtered_clean_data = clean_data[clean_data["code_sample_id"] == code_sample.id]
        aggregated_answer.n = len(filtered_clean_data)
        aggregated_answer.percent = (len(filtered_clean_data) / n_responses) * 100
        pass


class AggregatorType4(Aggregator):
    def execute(
        self,
        aggregated_answer,
        clean_data: pd.DataFrame,
        selected_lang: str,
        attribute: Attribute | None = None,
        code_sample: CodeSample | None = None,
    ):
        unique_values = clean_data["order"].unique()
        n_selected = {value: 0 for value in unique_values}
        for value in clean_data["order"]:
            n_selected[value] += 1
        weighted_order = pd.DataFrame(list(n_selected.items()), columns=["order", "n"])
        weighted_order["order"] = pd.to_numeric(weighted_order["order"])
        weighted_order["weighted"] = weighted_order["order"] * weighted_order["n"]
        aggregated_answer.order = n_selected
        aggregated_answer.weighted_order = float(weighted_order["weighted"].sum())
        pass


class AggregatedAnswer(AnswerBase):
    attribute_id: int | None
    attribute_order: int | None
    min: float | None
    max: float | None
    attribute_name: str | None
    attribute_lang: str | None
    user_id: UUID | None
    user_name: str | None
    code_sample_id: int | None
    sample_id: int | None
    code_sample_code: str | None
    code_sample_lang: str | None
    sample_name: str | None
    n: int | None
    percent: float | None
    text: str | None
    mean_order: float | None
    mean_value: float | None
    order: dict | None
    weighted_order: float | None
    placeholders: list["AggregatedPlaceholder"]
    aggregator: Aggregator | None = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, question=None, aggregator=None):
        self.placeholders = []
        if aggregator:
            self.set_aggregator(aggregator)
        else:
            selected_aggregator = self.select_aggregator(question)
            self.set_aggregator(selected_aggregator)

    def select_aggregator(self, question):
        if question.type == 1:
            return AggregatorType1()
        elif question.type == 2:
            return AggregatorType2()
        elif question.type == 3:
            if len(question.attributes) != 0:
                return AggregatorType3Attributes()
            else:
                return AggregatorType3Samples()
        elif question.type == 4:
            return AggregatorType4()

    def set_aggregator(self, aggregator):
        self.aggregator = aggregator

    def execute_aggregator(
        self,
        clean_data: pd.DataFrame,
        selected_lang: str,
        attribute: Attribute | None = None,
        code_sample: CodeSample | None = None,
    ):
        if self.aggregator is None:
            raise ValueError("aggregator not set")
        else:
            return self.aggregator.execute(
                self, clean_data, selected_lang, attribute, code_sample
            )


class AggregatedPlaceholder(AnswerBase):
    id: int
    order: int
    placeholder_name: str
    placeholder_lang: str
    n: int
    percent: float

    def __init__(self, placeholder, selected_lang, key, clean_data):
        translation = get_translation(
            placeholder, key="name", selected_lang=selected_lang
        )
        self.id = placeholder.id
        self.order = placeholder.order
        self.placeholder_name = translation.value
        self.placeholder_lang = translation.lang
        filtered_clean_data = clean_data[clean_data["placeholder_id"] == placeholder.id]
        self.n = len(filtered_clean_data)
        self.percent = (len(filtered_clean_data) / len(clean_data)) * 100


class StatTest(ABC):
    @abstractmethod
    def execute(self, stats: "Stats", clean_data: pd.DataFrame):
        pass


class Anova(StatTest):
    def execute(self, stats: "Stats", clean_data: pd.DataFrame):
        stats.attribute_id = int(clean_data["attribute_id"].unique()[0])
        try:
            model = ols(
                "placeholder_order ~ C(code_sample_id) + C(user_id)", data=clean_data
            ).fit()
            anova_table = sm.stats.anova_lm(model, typ=2)
            p_value = float(anova_table.loc["C(code_sample_id)", "PR(>F)"])
            stats.p_value = p_value
        except:
            stats.p_value = None
        try:
            clean_data["placeholder_name"] = pd.to_numeric(
                clean_data["placeholder_name"], errors="coerce"
            )
            model = ols(
                "placeholder_name ~ C(code_sample_id) + C(user_id)", data=clean_data
            ).fit()
            anova_table = sm.stats.anova_lm(model, typ=2)
            p_value = float(anova_table.loc["C(code_sample_id)", "PR(>F)"])
            stats.p_value_name = p_value
        except:
            stats.p_value_name = None


class TTest(StatTest):
    def execute(self, stats: "Stats", clean_data: pd.DataFrame):
        unique_code_samples = clean_data["code_sample_id"].unique()
        if len(unique_code_samples) < 2:
            return
        try:
            p_value_order = scipy_stats.ttest_rel(
                clean_data[clean_data["code_sample_id"] == unique_code_samples[0]][
                    "placeholder_order"
                ].values,
                clean_data[clean_data["code_sample_id"] == unique_code_samples[1]][
                    "placeholder_order"
                ].values,
            )
            p_ind = float(smm.multipletests([p_value_order.pvalue], method="holm")[1])
            stats.p_value = p_ind
        except:
            stats.p_value = None
        try:
            p_value_name = scipy_stats.ttest_rel(
                clean_data[clean_data["code_sample_id"] == unique_code_samples[0]][
                    "placeholder_name"
                ].values,
                clean_data[clean_data["code_sample_id"] == unique_code_samples[1]][
                    "placeholder_name"
                ].values,
            )
            p_ind_name = float(
                smm.multipletests([p_value_name.pvalue], method="holm")[1]
            )
            stats.p_value_name = p_ind_name
        except:
            stats.p_value_name = None


class ChiSquare(StatTest):
    def execute(self, stats: "Stats", clean_data: pd.DataFrame):
        question = stats.question
        if question.type == 3:
            if len(question.attributes) != 0:
                column_to_test = clean_data["attribute_id"]
            else:
                column_to_test = clean_data["code_sample_id"]
        elif question.type == 4:
            clean_data = clean_data[clean_data["order"] == 0]
            column_to_test = clean_data["code_sample_id"]
        try:
            observed = np.array(column_to_test)
            n = len(column_to_test)
            degrees_of_freedom = n - 1
            expected = np.full(n, np.mean(observed))
            chi_squared_stat = np.sum((observed - expected) ** 2 / expected)
            degrees_of_freedom = n - 1
            p_val = float(gammaincc(degrees_of_freedom / 2.0, chi_squared_stat / 2.0))
            stats.p_value = p_val
        except:
            stats.p_value = None


class Friedman(StatTest):
    def execute(self, stats: "Stats", clean_data: pd.DataFrame):
        try:
            pivot_df = clean_data.pivot(
                index="user_id", columns="code_sample_id", values="order"
            )
            pivot_df = pivot_df.dropna()
            grupos = [pivot_df[col].values for col in pivot_df.columns]
            p_value = float(scipy_stats.friedmanchisquare(*grupos).pvalue)
            stats.p_value = p_value
        except:
            stats.p_value = None


class Stats(AnswerBase):
    question: Question = Field(exclude=True)
    attribute_id: int | None
    p_value: float | None
    p_value_name: float | None
    stat_test: StatTest | None = Field(exclude=True)
    code_samples: list["CodeSample"] | None = Field(exclude=True)
    clean_data: pd.DataFrame | None = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        question,
        attribute_id=None,
        p_value=None,
        p_value_name=None,
        stat_test=None,
        code_samples=None,
    ):
        self.attribute_id = attribute_id
        self.question = question
        self.code_samples = code_samples
        if stat_test:
            self.set_stat_test(stat_test)
        else:
            selected_stat_test = self.select_stat_test(self.code_samples, self.question)
            self.set_stat_test(selected_stat_test)

    def select_stat_test(self, code_samples, question):
        if question.type == 1:
            if len(code_samples) > 2:
                return Anova()
            else:
                return TTest()
        elif question.type == 3:
            return ChiSquare()
        elif question.type == 4:
            if len(code_samples) < 2:
                return ChiSquare()
            else:
                return Friedman()

    def set_stat_test(self, stat_test):
        self.stat_test = stat_test

    def execute_test(self, clean_data: pd.DataFrame):
        if self.stat_test is not None:
            return self.stat_test.execute(self, clean_data)
