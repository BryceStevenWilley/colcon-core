
from collections import OrderedDict
import os
import types
import traceback

from colcon_core.argument_parser.destination_collector \
    import DestinationCollectorDecorator
from colcon_core.logging import colcon_logger
from colcon_core.package_selection import add_arguments \
    as add_packages_arguments
from colcon_core.package_selection import get_packages
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import logger
from colcon_core.verb import check_and_mark_build_tool
from colcon_core.verb import check_and_mark_install_layout
from colcon_core.verb import VerbExtensionPoint

def yes_no_loop(question):
    while True:
        resp = str(input(question + " [yN]: "))
        if resp.lower() in ['n', 'no'] or len(resp) == 0:
            return False
        elif resp.lower() in ['y', 'yes']:
            return True
        logger.info('Please answer either "yes" ("y") or "no" ("n").')

class CleanVerb(VerbExtensionPoint):
    """
    'Cleans' (uninstalls) an entire set of packages.
    """

    def __init__(self): # noqa: D107
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser): # noqa: D102
        # TODO(brycew): is this where profiles get set?
        parser.add_argument(
            '--build-base',
            default='build',
            help='The base path for all build directories (default: build)')
        parser.add_argument(
            '--install-base',
            default='install',
            help='The base path for all install prefixes (default: install)')
        parser.add_argument(
            '--dry-run', '-n', action='store_true', default=False,
            help='Show the effects of the clean action without modifying the workspace')
        parser.add_argument(
            '--yes', '-y', action='store_true', default=False,
            help='Assume "yes" to all interactive checks')

        add_packages_arguments(parser)

        decorated_parser = DestinationCollectorDecorator(parser)
        self.task_argument_destinations = decorated_parser.get_destinations()

    def main(self, *, context): #noqa: D102
        check_and_mark_build_tool(context.args.build_base)
        check_and_mark_install_layout(
            context.args.install_base,
            merge_install=False)

        decorators = get_packages(
            context.args,
            additional_argument_names=self.task_argument_destinations)


        jobs = self._get_jobs(context.args, decorators)
        logger.error("TODO(brycew): actually clean")
        return


    def _get_jobs(self, args, decorators):
        jobs = OrderedDict()
        for decorator in decorators:
            if not decorator.selected:
                continue
            pkg = decorator.descriptor
            logger.error("pkg: {pkg}".format_map(locals()))

        try:
            yes = yes_no_loop("\nAre you sure you want to completely remove the directories listed above?")
            if not yes:
                logger.info("Not removing any workspace directories for this profile")
                return
        except KeyboardInterrupt:
            logger.warn("No actions performed")

        return []
