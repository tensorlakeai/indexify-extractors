import inspect
from typing import Callable, List, Optional, get_type_hints

from .base_extractor import Content, Extractor


def extractor(
    name: Optional[str] = None,
    description: Optional[str] = "",
    version: Optional[str] = "",
    python_dependencies: Optional[List[str]] = None,
    system_dependencies: Optional[List[str]] = None,
    input_mime_types: Optional[List[str]] = None,
    sample_content: Optional[Callable] = None,
):
    args = locals()
    del args["sample_content"]

    def construct(fn):
        hint = get_type_hints(fn).get("params", dict)

        if not args.get("name"):
            args["name"] = (
                f"{inspect.getmodule(inspect.stack()[1][0]).__name__}:{fn.__name__}"
            )

        class DecoratedFn(Extractor):
            def extract(self, content: Content, params: hint) -> List[Content]:  # type: ignore
                return fn(content, params)

            def sample_input(self) -> Content:
                return sample_content() if sample_content else self.sample_text()

        for key, val in args.items():
            setattr(DecoratedFn, key, val)

        return DecoratedFn

    return construct
