import seldon.core.cli
import seldon.action.commands.action

class ActionCLI(seldon.core.cli.CLI):
  def main_class(self):
    """Override this with a class containing the commands that need running"""
    return seldon.action.commands.action.ActionCommands

  def add_tree(self):
    """Create a randomly generated data set to test things out with"""
    defs = {

    }
    sub = self.subparsers.add_parser('tree', help="grow a tree")
    sub.add_argument(
      "--depth",
      help="the maximum depth of the tree (default: %(default)s)",
      default=10,
      type=int
    )
    sub.add_argument(
      "--size",
      help="the smallest size of terminal nodes with values less than zero as fractions of whole training set (default: %(default)s)",
      default=0.01,
      type=float
    )
    k = "min-category"
    sub.add_argument(
      '--' + k,
      help="the minimum number or fraction of records for a category to count (default: %(default)s)",
      default=defs.get(k, 0.1),
      type=float
    )

    k = "max-ordinality"
    sub.add_argument(
      '--' + k,
      help="the maximum number or fraction of categories to count (default: %(default)s)",
      default=defs.get(k, 10),
      type=float
    )

    k = "z-score"
    sub.add_argument(
      '--' + k,
      help="the minimum z-score to consider significant (default: %(default)s)",
      default=defs.get(k, 5),
      type=int
    )

    sub.add_argument(
      "--cutoff",
      help="the minimum average value for terminal nodes (default: %(default)s)",
      default=0.3333,
      type=float
    )

    k = "fpr"
    sub.add_argument(
      '--' + k,
      help="the maximum fpr, used instead of cutoff if it is not None (default: %(default)s)",
      default=defs.get(k, None),
      type=float
    )

    k = "cutoff-mode"
    sub.add_argument(
      '--' + k,
      help="set the fraud rate cutoff by authorizations, dollars, or accounts (default: %(default)s)",
      default=defs.get(k, 'authorizations'),
    )

    k = "mode"
    sub.add_argument(
      '--' + k,
      help="the mode for splits, must be in authorizations, dollars, loss (default: %(default)s)",
      default=defs.get(k, 'authorizations'),
    )

    k = "drops"
    sub.add_argument(
      '--' + k,
      help="a comma-delimeted list of feature columns to drop from the model (default: %(default)s)",
      default=defs.get(k, ''),
    )

    k = "keeps"
    sub.add_argument(
      '--' + k,
      help="a comma-delimeted list of feature columns to keep for the model, all others dropped (default: %(default)s)",
      default=defs.get(k, ''),
    )

    k = "min-entities"
    sub.add_argument(
      # the minimum number of accounts to be allowed for a split
      # fraud accounts for the high-fraud branch, good accounts for the low-fraud branch
      '--' + k,
      help="smallest number of entities [good for low-value branch, bad for high-value branch] for split (default: %(default)s)",
      default=defs.get(k, 0),
      type=int
    )

    k = "processes"
    sub.add_argument(
      '--' + k,
      help="the maximum number of processes to use for splits (default: %(default)s)",
      default=defs.get(k, 100),
      type=int
    )

    self.cmd_standard(sub, func=lambda command_class, path: command_class.cmd_train(path))


