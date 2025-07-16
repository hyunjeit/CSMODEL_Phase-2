import itertools
import pandas as pd

class RuleMiner(object):

    def __init__(self, support_t, confidence_t):
        self.support_t = support_t
        self.confidence_t = confidence_t

    def get_support(self, data, itemset):
        itemset = list(itemset)
        return data[itemset].all(axis=1).sum()

    def merge_itemsets(self, itemsets):
        new_itemsets = []

        cur_num_items = len(itemsets[0])

        if cur_num_items == 1:
            for i in range(len(itemsets)):
                for j in range(i + 1, len(itemsets)):
                    new_itemsets.append(list(set(itemsets[i]) | set(itemsets[j])))

        else:
            for i in range(len(itemsets)):
                for j in range(i + 1, len(itemsets)):
                    combined_list = list(set(itemsets[i]) | set(itemsets[j]))
                    combined_list.sort()
                    if len(combined_list) == cur_num_items + 1 and combined_list not in new_itemsets:
                        new_itemsets.append(combined_list)

        return new_itemsets

    def get_rules(self, itemset):
        combinations = itertools.combinations(itemset, len(itemset) - 1)
        combinations = [list(combination) for combination in combinations]

        rules = []
        for combination in combinations:
            diff = set(itemset) - set(combination)
            rules.append([combination, list(diff)])
            rules.append([list(diff), combination])

        return rules

    def get_frequent_itemsets(self, data):
        itemsets = [[i] for i in data.columns]
        old_itemsets = []
        flag = True

        while flag:
            new_itemsets = []
            for itemset in itemsets:
                support = self.get_support(data, itemset)
                if support >= self.support_t:
                    new_itemsets.append(itemset)

            if len(new_itemsets) != 0:
                old_itemsets = new_itemsets
                itemsets = self.merge_itemsets(new_itemsets)
            else:
                flag = False
                itemsets = old_itemsets

        return itemsets

    def get_confidence(self, data, rule):
        X, y = rule

        if not isinstance(X, list):
            X = [X]

        if isinstance(y, list):
            if len(y) == 1:
                y = y[0]

        support_Xy = self.get_support(data, X + [y])
        support_X = self.get_support(data, X)
    
        if support_X == 0:
            return 0.0
    
        confidence = support_Xy / support_X
        return confidence

    def get_association_rules(self, data):
        itemsets = self.get_frequent_itemsets(data)
        
        rules = []
        for itemset in itemsets:
            rules.extend(self.get_rules(itemset))

        association_rules = []
        for rule in rules:
            X, y = rule

            if isinstance(y, list):
                if len(y) != 1:
                    continue
                y = y[0]
        
            confidence = self.get_confidence(data, [X, y])
            if confidence >= self.confidence_t and "INCOME_BRACKET" in str(y):
                association_rules.append([X, y])

        return association_rules
    
    def extract_income_rules(self, data, antecedent_col, consequent_col='INCOME_BRACKET'):

        df_pair = data[[antecedent_col, consequent_col]]
        df_encoded = pd.get_dummies(df_pair).astype(int)

        rules = self.get_association_rules(df_encoded)

        for rule in rules:
            X, y = rule
            if consequent_col in str(y) and not any(consequent_col in str(x) for x in X):
                confidence = self.get_confidence(df_encoded, [X, y])
                antecedent = " + ".join(X) if isinstance(X, list) else str(X)
                print(f"IF {antecedent} → THEN {y} | Confidence: {confidence:.2f}")
