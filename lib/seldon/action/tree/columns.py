import seldon.core.spark

from seldon.core.objects import properties, self_properties


class ColumnException(Exception): pass


class Column:
  # https://mnesarco.github.io/blog/2020/07/23/python-metaprogramming-properties-on-steroids
  with properties(locals(), 'meta') as meta:
    @meta.prop(read_only=True)
    def root(self) -> str:
      """root path"""

    @meta.prop(read_only=True)
    def name(self) -> str:
      """column name"""

    @meta.prop(read_only=True)
    def categorical(self) -> bool:
      """is the column a categorical?"""

    @meta.prop(read_only=True)
    def data(self):
      """column data describing mapping and percentile information"""
      return None

  def __init__(self, name, root, categorical):
    """Create the column
    root_path - where the column data is stored
    name - the name of the column
    column_type - numerical or categorical
    """
    self_properties(self, locals())

  def path(self):
    return os.path.join(self.root, self.name + 'parquet')

  def create(self, data, max_categories, min_records):
    """Create the mapping table
    data is a dataframe with
     - value   - the value of the feature
     - weight  - how many instances this record represents
     - outcome - may be 0/1 or a continuous outcome (like a cost of this event)
    max_categories is the maximum number of distinct categories to keep
    min_records is the smallest number of records in a category to keep (or fraction is min_records is less than 1)
    """

    # make sure we have default weights as well
    if 'weight' not in data.columns: data = data.withColumn('weight', F.lit(1))

    # default to having outcome_effective equal to outcome
    effective = data.withColumn('value_effective', F.col('outcome'))

    # the categoricals require some fancy transforms to get a numerical equivelent
    if self.type == 'categorical':
      # update output_effective for the categoricals

      # first get the average outcome for each value
      effective = effective.groupBy(
        'value'
      ).agg(
        F.sum('weight').alias('n'),
        F.sum(F.col('outcome') * F.col('weight')).alias('outcome'),
      ).withColumn(
        'outcome_bar',
        F.col('outcome') / F.col('n'),
      ).orderBy(
        'outcome_bar'
      ).withColumn(
        'change',
        F.when(
          # mark the infrequent ones for change
          F.col('n') < min_records,
          1
        ).otherwise(
          # everyone else MIGHT be kept as is
          0
        )
      )

      # of the frequents, we cannot take too many
      # so sort candidates in order. And the outer ones are the ones to keep (in place of the ones in the middle)
      frequents = effective.where(F.col('change') == 0)
      if len(frequents) == 0: raise ColumnException("no categories where # records >= {min_records}")
      candidates = [[r.outcome_bar, r.value] for r in effective.collect()]
      candidates = sorted(candidates, key=lambda r: r[0], reverse=True)
      keep = []
      while len(keep) < max_categories and len(candidates) > 0:
        # look for the most extreme (outlying) and take the middle ones only as a last resort
        i = 0 if len(keep) % 2 == 0 else -1
        keep.append(candidates[i][1])
        del (candidates[i])
      effective = effective.withColumn(
        # only the ones in keep are NOT marked for change
        'change',
        F.when(
          F.col('value').isin(keep),
          0
        ).otherwise(
          1
        )
      )

      # get the average of all the outcomes for the ones marked for change
      # and then update the changed ones with this global average outcome
      change_outcome = effective.where(
        F.col('change') == 1
      ).agg(
        (F.sum('outcome') / F.sum('n')).alias('outcome')
      ).collect()[0].outcome
      effective = effective.withColumn(
        'value_effective',
        F.when(
          F.col('change') == 1,
          change_outcome
        ).otherwise(
          F.col('outcome_bar')
        )
      )  # .select('value', 'value_effective')
      print(effective)
      sys.exit()

    # effective_to_values = effective.groupBy(
    #   'value_effective'
    # ).agg(
    #   F.collectSet('value')
    # )

    # then do percentiles

    # do percentiles for each value

    # sums so we can do percents
    # g = data.agg(
    #   F.sum('weight').alias('n'),
    #   F.sum(F.col('outcome') * F.col('weight')).alias('sum_outcome'),
    # ).collect()[0]
    # if min_records < 1: min_records *= min_records

    if self.type != 'categorical': raise ColumnException("create can only be called for categorical values")
    pass

  def load(self, force=False):
    """Load the column data from disk"""
    if force:  # noinspection PyAttributeOutsideInit
      self.data = None
    if self.data is None:  # noinspection PyAttributeOutsideInit
      self._data = seldon.core.spark().load.parquet(self.path())
    return self.data

  def save(self):
    """Save the column data to disk in the standard location"""
    if self.data is None: raise ColumnException("Cannot save column unless it is created or loaded first")
    self.data.write.mode('overwrite').parquet(self.data)

  def from_numerical(self, value):
    """Convert a feature value to the categorical matches or leave it as a numerical value if this is a numerical column"""
    if self.type != 'categorical': return value

    pass

  # noinspection PyMethodMayBeStatic
  def to_percentile(self, value):
    """Convert a column value to the min and max percentile of that value"""
    return value

  def percentile_distance(self, value1, value2):
    p1 = self.to_percentile(value1)
    p2 = self.to_percentile(value2)
    if p1[0] == p2[0]: return [0, p2[1] - p1[0]]
    if p1[0] < p2[0]: return [p2[0] - p1[0], p2[0] - p1[1]]
    if p2[0] < p1[0]: return [p2[0] - p1[0], p2[0] - p1[1]]
    return []

  def to_rule(self, comparator, cutoff):
    """Convert a numerical comparison to either
    - the same if this is a numerical column
    - the categorical version if this is a categorical colum
    """
    if self.type == 'numerical': return f'{self.name} {comparator} {cutoff}'
    raise ColumnException("Have not finished categorical for to_rule")
    # chose the smallest side, adding not as needed

  def distance_to_cutoff(self, value, cutoff):
    """Get the percentile change in this value to reach the cutoff value"""
    pass
