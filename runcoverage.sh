coverage run -m unittest tests.classes.semiring.SemiringBasicProperties
mv .coverage .coverage.SemiringBasicProperties
coverage run -m unittest tests.classes.graph.GraphBasicProperties
mv .coverage .coverage.GraphBasicProperties
coverage combine
coverage report --show-missing
