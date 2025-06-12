from types import MethodType
from typing import Any, Iterator, overload

from pydantic import BaseModel

from fundamend.models import anwendungshandbuch as ahb
from fundamend.models import messageimplementationguide as mig

TRAVERSE_FIELD_NAMES = {
    ahb.Anwendungshandbuch: "anwendungsfaelle",
    ahb.Anwendungsfall: "elements",
    ahb.SegmentGroup: "elements",
    ahb.Segment: "data_elements",
    ahb.DataElementGroup: "data_elements",
    ahb.DataElement: "codes",
    mig.MessageImplementationGuide: "elements",
    mig.SegmentGroup: "elements",
    mig.Segment: "data_elements",
    mig.DataElementGroup: "data_elements",
    mig.DataElement: "codes",
}
SEGMENT_INDEX_AHB = dict[str, ahb.Segment]
SEGMENT_INDEX_MIG = dict[str, mig.Segment]


def _disabled_hash(_) -> int:
    raise ValueError("Hash function is disabled for this model as some attribute was overridden by object.__setattr__.")


def _set(model: BaseModel, field_name: str, field_value: Any) -> None:
    object.__setattr__(model, field_name, field_value)
    model.__hash__ = MethodType(_disabled_hash, model)  # type: ignore[method-assign]
    # This hash function override is just for our safety to prevent obscure errors when trying to use
    # the model as a hashable object.


def segment_number_search_index(
    root: ahb.Anwendungsfall | mig.MessageImplementationGuide | ahb.SegmentGroup | mig.SegmentGroup,
) -> SEGMENT_INDEX_AHB | SEGMENT_INDEX_MIG:
    """
    Creates a search index for segment numbers in the given AHB or MIG root.
    The index maps segment numbers to their position in the root's elements list.
    """
    index = {}
    for element in root.elements:
        if isinstance(element, (ahb.Segment, mig.Segment)):
            assert (
                element.number not in index
            ), f"Duplicate segment number found: {element.number} in {root.__class__.__name__}"
            index[element.number] = element
        if isinstance(element, (ahb.SegmentGroup, mig.SegmentGroup)):
            sub_index = segment_number_search_index(element)
            assert all(
                sub_key not in index for sub_key in sub_index
            ), f"Duplicate segment number found in sub-index: {list(sub_index.keys())} in {root.__class__.__name__}"
            index.update(sub_index)
    return index


def match_ahb_data_element_with_mig_data_element(
    mig_data_element: mig.DataElement, ahb_data_element: ahb.DataElement
) -> bool:
    """
    Check if the given AHB or MIG data element matches the MIG data element.

    :param ahb_data_element: The AHB or MIG data element to check.
    :param mig_data_element: The MIG data element to check against.
    :return: ``True`` if the AHB element matches the MIG data element, ``False`` otherwise.
    """
    return (
        ahb_data_element.id == mig_data_element.id
        and ahb_data_element.name == mig_data_element.name
        and set(code.value for code in ahb_data_element.codes) <= set(code.value for code in mig_data_element.codes)
    )


def match_ahb_data_element_group_with_mig_data_element_group(
    mig_data_element_group: mig.DataElementGroup, ahb_data_element_group: ahb.DataElementGroup
) -> bool:
    """
    Check if the given AHB data element group matches the MIG data element group.

    :param ahb_data_element_group: The AHB data element group to check.
    :param mig_data_element_group: The MIG data element group to check against.
    :return: ``True`` if the AHB data element group matches the MIG data element group, ``False`` otherwise.
    """
    _has_same_id = ahb_data_element_group.id == mig_data_element_group.id
    if not _has_same_id:
        return False
    _all_data_elements_in_mig_data_element_group = all(
        any(
            match_ahb_data_element_with_mig_data_element(ahb_data_element, mig_data_element)
            for mig_data_element in mig_data_element_group.data_elements
        )
        for ahb_data_element in ahb_data_element_group.data_elements
    )
    return _all_data_elements_in_mig_data_element_group


@overload
def parallel_iter_segment_or_data_element_group(
    mig_segment_or_group: mig.Segment, ahb_segment_or_group: ahb.Segment
) -> Iterator[
    tuple[mig.DataElementGroup, ahb.DataElementGroup | None] | tuple[mig.DataElement, ahb.DataElement | None]
]: ...


@overload
def parallel_iter_segment_or_data_element_group(
    mig_segment_or_group: mig.DataElementGroup, ahb_segment_or_group: ahb.DataElementGroup
) -> Iterator[tuple[mig.DataElement, ahb.DataElement | None]]: ...


@overload
def parallel_iter_segment_or_data_element_group(
    mig_segment_or_group: mig.Segment | mig.DataElementGroup, ahb_segment_or_group: ahb.Segment | ahb.DataElementGroup
) -> Iterator[
    tuple[mig.DataElementGroup, ahb.DataElementGroup | None] | tuple[mig.DataElement, ahb.DataElement | None]
]: ...


def parallel_iter_segment_or_data_element_group(
    mig_segment_or_group: mig.Segment | mig.DataElementGroup, ahb_segment_or_group: ahb.Segment | ahb.DataElementGroup
) -> Iterator[
    tuple[mig.DataElementGroup, ahb.DataElementGroup | None] | tuple[mig.DataElement, ahb.DataElement | None]
]:
    """
    If a element is unused in AHB, i.e. if it has MigStatus.N or if it is part of a degenerated element set which
    would result in an IndexError, the MIG element will be yielded with ``None`` as the AHB counterpart.
    """
    assert len(mig_segment_or_group.data_elements) > 0 and len(ahb_segment_or_group.data_elements) > 0
    mig_elements = iter(mig_segment_or_group.data_elements)
    ahb_elements = iter(ahb_segment_or_group.data_elements)

    cur_mig_element = next(mig_elements)
    cur_ahb_element = next(ahb_elements)

    while True:
        if isinstance(cur_mig_element, mig.DataElement):
            ahb_match = isinstance(cur_ahb_element, ahb.DataElement) and match_ahb_data_element_with_mig_data_element(
                cur_ahb_element, cur_mig_element
            )
        else:
            assert isinstance(cur_mig_element, mig.DataElementGroup)
            ahb_match = isinstance(
                cur_ahb_element, ahb.DataElementGroup
            ) and match_ahb_data_element_group_with_mig_data_element_group(cur_ahb_element, cur_mig_element)
        if ahb_match:
            yield cur_mig_element, cur_ahb_element
            cur_ahb_element = next(ahb_elements, None)
        else:
            yield cur_mig_element, None
        try:
            cur_mig_element = next(mig_elements)
        except StopIteration:
            break
    try:
        next(ahb_elements)
        raise ValueError(
            f"AHB segment or group {ahb_segment_or_group.id} has more data elements than "
            f"MIG segment or group {mig_segment_or_group.id}."
        )
    except StopIteration:
        pass


def create_ahb_data_element_from_mig(mig_data_element: mig.DataElement) -> ahb.DataElement:
    """
    Creates an AHB data element from a MIG data element.
    This is used to add unused MIG data elements to the AHB.
    """
    assert len(mig_data_element.codes) == 0, "Expected MIG data element to have no codes if it is unused in AHB."
    return ahb.DataElement(
        id=mig_data_element.id,
        name=mig_data_element.name,
        ahb_status="X [2499]",
        codes=(),
    )


def create_ahb_data_element_group_from_mig(mig_data_element_group: mig.DataElementGroup) -> ahb.DataElementGroup:
    """
    Creates an AHB data element group from a MIG data element group.
    This is used to add unused MIG data element groups to the AHB.
    """
    return ahb.DataElementGroup(
        id=mig_data_element_group.id,
        name=mig_data_element_group.name,
        data_elements=tuple(
            create_ahb_data_element_from_mig(mig_data_element)
            for mig_data_element in mig_data_element_group.data_elements
        ),
    )


def add_unused_elements_to_ahb_elements(
    mig_element: mig.Segment | mig.DataElementGroup, ahb_element: ahb.Segment | ahb.DataElementGroup
) -> None:
    """
    Adds unused MIG data elements to the AHB data element group.
    This ensures that all MIG elements are present in the AHB for parallel iteration.
    """
    edited_ahb_elements = list(ahb_element.data_elements)
    for index, (cur_mig_element, cur_ahb_element) in enumerate(
        parallel_iter_segment_or_data_element_group(mig_element, ahb_element)
    ):
        if cur_ahb_element is None:
            # MIG element is unused in AHB, add it to AHB
            if isinstance(cur_mig_element, mig.DataElement):
                edited_ahb_elements.insert(index, create_ahb_data_element_from_mig(cur_mig_element))
            else:
                assert isinstance(cur_mig_element, mig.DataElementGroup)
                edited_ahb_elements.insert(index, create_ahb_data_element_group_from_mig(cur_mig_element))
        elif isinstance(cur_mig_element, mig.DataElementGroup):
            assert isinstance(cur_ahb_element, ahb.DataElementGroup)
            add_unused_elements_to_ahb_elements(cur_mig_element, cur_ahb_element)
    _set(ahb_element, "data_elements", tuple(edited_ahb_elements))
    assert len(ahb_element.data_elements) == len(mig_element.data_elements)


def add_unused_elements_to_ahb(mig_segment_index: SEGMENT_INDEX_MIG, ahb_segment_index: SEGMENT_INDEX_AHB) -> None:
    """
    Adds unused MIG data elements and groups to the AHB segment index.
    This ensures that all MIG elements are present in the AHB for parallel iteration.
    """
    for number, mig_segment in mig_segment_index.items():
        ahb_segment = ahb_segment_index[number]
        add_unused_elements_to_ahb_elements(mig_segment, ahb_segment)


def add_must_not_pattern_to_ahb_conditions(ahb_root: ahb.Anwendungshandbuch) -> None:
    for condition in ahb_root.bedingungen:
        if condition.nummer == "2499":
            raise ValueError(
                "Condition 2499 is used as a must-not pattern after sanitization of the AHB. "
                "Please check the AHB for correctness."
            )
    _set(
        ahb_root,
        "bedingungen",
        ahb_root.bedingungen
        + (
            ahb.Bedingung(
                nummer="2499",
                text='Ist immer falsch, um ein "Darf nicht" pattern umzusetzen: "X [2499]". '
                'Diese Expression wird für u.a. für Elemente genutzt, die laut MIG "unused" sind.',
            ),
        ),
    )


def sanitize_ahb(ahb_root: ahb.Anwendungshandbuch, mig_root: mig.MessageImplementationGuide) -> None:
    """
    Sanitizes the AHB by adding unused MIG data elements and groups to the AHB.
    """
    add_must_not_pattern_to_ahb_conditions(ahb_root)
    for anwendungsfall in ahb_root.anwendungsfaelle:
        mig_search_index = segment_number_search_index(mig_root)
        ahb_search_index = segment_number_search_index(anwendungsfall)
        add_unused_elements_to_ahb(mig_search_index, ahb_search_index)
