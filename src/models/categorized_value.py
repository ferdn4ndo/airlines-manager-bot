from models.base_model import BaseModel


class CategorizedValue(BaseModel):
    """
    Model class (to be inherited) representing a CategorizedValue resource
    """
    economic = 0
    executive = 0
    first_class = 0
    cargo = 0

    serializable_fields = ['economic', 'executive', 'first_class', 'cargo']

    def __str__(self):
        """
        Overrides the original string conversion method to retrieve the total sum of internal values instead
        :return:
        """
        return '{}'.format(self.economic + self.executive + self.first_class + self.cargo)

    def __eq__(self, other: "CategorizedValue"):
        """
        Overrides the original comparison method to compare by checking each group difference
        :param other:
        :return:
        """
        economic_diff = abs(self.economic - other.economic)
        executive_diff = abs(self.executive - other.executive)
        first_class_diff = abs(self.first_class - other.first_class)
        cargo_diff = abs(self.cargo - other.cargo)

        return (economic_diff + executive_diff + first_class_diff + cargo_diff) == 0
