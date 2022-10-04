import seldon.core.cli
import seldon.burke.commands.disease

class BurkeCLI(seldon.core.cli.CLI):
  def main_class(self):
    """Override this with a class containing the commands that need running"""
    return seldon.burke.commands.disease.DiseaseCommands

  def add_disease_cache(self):
    """Scrape the web for the rare disease data base"""
    sub = self.subparsers.add_parser('cache-disease', help="scrape rare disease data sets")

    defs = {
      'data-root': seldon.core.path.join('~/seldon/data')
    }

    k = 'data-root'
    sub.add_argument(
      "--" + k,
      help="where the cache data is stored (default: %(default)s)",
      default=defs.get(k, 10),
      type=int
    )

    # no path arguments
    self.unpathed.append(name)
    self.cmd_standard(sub, func=lambda command_class: command_class.command_disease_cache())

  def add_drug_cache(self):
    """Scrape the FDA website for drug usage"""
    sub = self.subparsers.add_parser('cache-drug', help="scrape FDA drug approval")

    defs = {
      'data-root': seldon.core.path.join('~/seldon/data')
    }

    k = 'data-root'
    sub.add_argument(
      "--" + k,
      help="where the cache data is stored (default: %(default)s)",
      default=defs.get(k, 10),
      type=int
    )

    # no path arguments
    self.unpathed.append(name)
    self.cmd_standard(sub, func=lambda command_class: command_class.command_drug_cache())

