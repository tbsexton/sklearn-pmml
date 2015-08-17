from unittest import TestCase

import numpy as np
from jpmml_test import JPMMLClassificationTest, JPMMLRegressionTest

from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from sklearn_pmml.convert import TransformationContext, pmml_row
from sklearn_pmml.convert.features import *
from sklearn_pmml.convert.tree import DecisionTreeConverter
from sklearn_pmml import pmml

from unittest import TestCase


class TestDecisionTreeClassifierConverter(TestCase):
    def setUp(self):
        np.random.seed(1)
        self.est = DecisionTreeClassifier(max_depth=2)
        self.est.fit([
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1],
        ], [0, 1, 1, 1])
        self.ctx = TransformationContext(
            input=[IntegerNumericFeature('x1'), StringCategoricalFeature('x2', ['zero', 'one'])],
            model=[IntegerNumericFeature('x1'), StringCategoricalFeature('x2', ['zero', 'one'])],
            derived=[],
            output=[IntegerCategoricalFeature('output', ['neg', 'pos'])]
        )
        self.converter = DecisionTreeConverter(
            estimator=self.est,
            context=self.ctx,
            mode=DecisionTreeConverter.MODE_CLASSIFICATION
        )

    def test_transform(self):
        p = self.converter.pmml()
        tm = p.TreeModel[0]
        assert tm.MiningSchema is not None, 'Missing mining schema'
        assert len(tm.MiningSchema.MiningField) == 3, 'Wrong number of mining fields'
        assert tm.Node is not None, 'Missing root node'
        assert tm.Node.recordCount == 4
        assert tm.Node.True_ is not None, 'Root condition should always be True'

    def test_transform_with_derived_field(self):
        self.est = DecisionTreeClassifier(max_depth=2)
        self.est.fit([
            [0, 0, 0],
            [0, 1, 0],
            [1, 0, 0],
            [1, 1, 1],
        ], [0, 1, 1, 1])
        mapping = pmml.MapValues(dataType="double", outputColumn="output")
        mapping.append(pmml.FieldColumnPair(column="x1", field="x1"))
        mapping.append(pmml.FieldColumnPair(column="x2", field="x2"))
        it = pmml.InlineTable()
        it.append(pmml_row(x1=0, x2='zero', output=0))
        it.append(pmml_row(x1=0, x2='one', output=0))
        it.append(pmml_row(x1=1, x2='zero', output=0))
        it.append(pmml_row(x1=1, x2='one', output=1))
        mapping.append(it)
        self.ctx = TransformationContext(
            input=[
                IntegerNumericFeature('x1'),
                StringCategoricalFeature('x2', ['zero', 'one']),
            ],
            derived=[
                DerivedFeature(
                    feature=RealNumericFeature(name='x3'),
                    transformation=mapping
                )
            ],
            model=[
                IntegerNumericFeature('x1'),
                StringCategoricalFeature('x2', ['zero', 'one']),
                RealNumericFeature(name='x3')
            ],
            output=[IntegerCategoricalFeature('output', ['neg', 'pos'])]
        )
        self.converter = DecisionTreeConverter(
            estimator=self.est,
            context=self.ctx,
            mode=DecisionTreeConverter.MODE_CLASSIFICATION
        )
        self.converter.pmml().toxml()


class TestDecisionTreeRegressorConverter(TestCase):
    def setUp(self):
        np.random.seed(1)
        self.est = DecisionTreeRegressor(max_depth=2)
        self.est.fit([
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1],
        ], [0, 1, 1, 1])
        self.ctx = TransformationContext(
            input=[IntegerNumericFeature('x1'), StringCategoricalFeature('x2', ['zero', 'one'])],
            model=[IntegerNumericFeature('x1'), StringCategoricalFeature('x2', ['zero', 'one'])],
            derived=[],
            output=[IntegerNumericFeature('output')]
        )
        self.converter = DecisionTreeConverter(
            estimator=self.est,
            context=self.ctx,
            mode=DecisionTreeConverter.MODE_REGRESSION
        )

    def test_transform(self):
        p = self.converter.pmml()
        tm = p.TreeModel[0]
        assert tm.MiningSchema is not None, 'Missing mining schema'
        assert len(tm.MiningSchema.MiningField) == 3, 'Wrong number of mining fields'
        assert tm.Node is not None, 'Missing root node'
        assert tm.Node.recordCount == 4
        assert tm.Node.True_ is not None, 'Root condition should always be True'


class TestDecisionTreeClassificationJPMMLParity(TestCase, JPMMLClassificationTest):

    def setUp(self):
        self.model = DecisionTreeClassifier()
        super(TestDecisionTreeClassificationJPMMLParity, self).init_data()
        super(TestDecisionTreeClassificationJPMMLParity, self).setUp()
        self.converter = DecisionTreeConverter(
            estimator=self.model,
            context=self.ctx,
            mode=DecisionTreeConverter.MODE_CLASSIFICATION
        )

class TestDecisionTreeRegressionJPMMLParity(TestCase, JPMMLRegressionTest):

    def setUp(self):
        self.model = DecisionTreeRegressor()
        super(TestDecisionTreeRegressionJPMMLParity, self).init_data()
        super(TestDecisionTreeRegressionJPMMLParity, self).setUp()
        self.converter = DecisionTreeConverter(
            estimator=self.model,
            context=self.ctx,
            mode=DecisionTreeConverter.MODE_REGRESSION
        )
