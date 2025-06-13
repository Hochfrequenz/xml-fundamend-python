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


@overload
def leading_segment(segment_group: ahb.SegmentGroup) -> ahb.Segment: ...


@overload
def leading_segment(segment_group: mig.SegmentGroup) -> mig.Segment: ...


def leading_segment(
    segment_group: ahb.SegmentGroup | mig.SegmentGroup,
) -> ahb.Segment | mig.Segment:
    """
    Return the first segment of the segment group.

    :param segment_group: The segment group.
    :returns: The first segment of the segment group.
    :raises TypeError: If the segment group doesn't start with a segment. This shouldn't happen if our assumptions are
        correct.
    """

    if not isinstance(segment_group.elements[0], (ahb.Segment, mig.Segment)):
        raise TypeError(
            f"Expected segment group to start with a segment, got {type(segment_group.elements[0])} instead."
        )
    return segment_group.elements[0]  # type: ignore[return-value]


def get_number(obj: mig.SegmentGroup | mig.Segment | ahb.SegmentGroup | ahb.Segment) -> str:
    """
    Get the number of the given segment or segment group.

    In case of a segment group, the number of the leading segment is returned.

    :param obj: The object to get the number from.
    :returns: The number of the segment or the segment groups leading segment.
    :raises ValueError: If the object type is unexpected.
    """
    match obj:
        case mig.SegmentGroup() | ahb.SegmentGroup():
            return leading_segment(obj).number
        case mig.Segment() | ahb.Segment():
            return obj.number
        case _:
            raise ValueError(f"Unexpected object type: {type(obj)}")


def match_ahb_data_element_with_mig_data_element(
    mig_data_element: mig.DataElement, ahb_data_element: ahb.DataElement
) -> bool:
    """
    Check if the given AHB or MIG data element matches the MIG data element.

    :param ahb_data_element: The AHB or MIG data element to check.
    :param mig_data_element: The MIG data element to check against.
    :return: ``True`` if the AHB element matches the MIG data element, ``False`` otherwise.
    """
    return ahb_data_element.id == mig_data_element.id


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
            match_ahb_data_element_with_mig_data_element(mig_data_element, ahb_data_element)
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
    assert len(mig_segment_or_group.data_elements) > 0
    # assert len(mig_segment_or_group.data_elements) > 0 and len(ahb_segment_or_group.data_elements) > 0
    # This assertion doesn't have to always hold. Counter example:
    # ORDERS 17112 G_SG29 LIN'00072'
    mig_elements = iter(mig_segment_or_group.data_elements)
    ahb_elements = iter(ahb_segment_or_group.data_elements)

    cur_mig_element = next(mig_elements)
    cur_ahb_element = next(ahb_elements, None)

    while True:
        if isinstance(cur_mig_element, mig.DataElement):
            ahb_match = isinstance(cur_ahb_element, ahb.DataElement) and match_ahb_data_element_with_mig_data_element(
                cur_mig_element, cur_ahb_element
            )
        else:
            assert isinstance(cur_mig_element, mig.DataElementGroup)
            ahb_match = isinstance(
                cur_ahb_element, ahb.DataElementGroup
            ) and match_ahb_data_element_group_with_mig_data_element_group(cur_mig_element, cur_ahb_element)
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


def parallel_iter_segment_group_or_root(
    mig_segment_group_or_root: mig.MessageImplementationGuide | mig.SegmentGroup,
    ahb_segment_group_or_root: ahb.Anwendungshandbuch | ahb.SegmentGroup,
) -> Iterator[tuple[mig.SegmentGroup, ahb.SegmentGroup | None] | tuple[mig.Segment, ahb.Segment | None]]:
    assert len(mig_segment_group_or_root.elements) > 0 and len(ahb_segment_group_or_root.elements) > 0
    mig_elements = iter(mig_segment_group_or_root.elements)
    ahb_elements = iter(ahb_segment_group_or_root.elements)

    cur_mig_element = next(mig_elements)
    cur_ahb_element = next(ahb_elements)

    while True:
        mig_number = get_number(cur_mig_element)
        ahb_number = cur_ahb_element and get_number(cur_ahb_element)
        if mig_number == ahb_number:
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
        ahb_element_id = (
            f"{ahb_segment_group_or_root.id}'{get_number(ahb_segment_group_or_root)}'"
            if isinstance(ahb_segment_group_or_root, ahb.SegmentGroup)
            else f"root"
        )
        mig_element_id = (
            f"{mig_segment_group_or_root.id}'{get_number(mig_segment_group_or_root)}'"
            if isinstance(mig_segment_group_or_root, mig.SegmentGroup)
            else f"root"
        )
        raise ValueError(f"AHB {ahb_element_id} has more elements than MIG {mig_element_id}.")
    except StopIteration:
        pass


def create_ahb_data_element_from_mig(mig_data_element: mig.DataElement) -> ahb.DataElement:
    """
    Creates an AHB data element from a MIG data element.
    This is used to add unused MIG data elements to the AHB.
    """
    # Sometimes a MIG data element can have a list of codes, but is still unused in the AHB. An example for this is
    # CONTRL UCI D_0085
    # In this case, we still don't add the codes to the AHB data element, because the data element will be forbidden
    # by the AHB expression anyway.
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


def create_ahb_segment_from_mig(mig_segment: mig.Segment) -> ahb.Segment:
    """
    Creates an AHB segment from a MIG segment.
    This is used to add unused MIG segments to the AHB.
    """
    return ahb.Segment(
        id=mig_segment.id,
        name=mig_segment.name,
        number=mig_segment.number,
        ahb_status="X [2499]",
        data_elements=(),
        # We don't need to add data elements here, because an application can detect the unused segment here and
        # stop further traversal.
    )


def create_ahb_segment_group_from_mig(mig_segment_group: mig.SegmentGroup) -> ahb.SegmentGroup:
    """
    Creates an AHB segment from a MIG segment.
    This is used to add unused MIG segments to the AHB.
    """
    return ahb.SegmentGroup(
        id=mig_segment_group.id,
        name=mig_segment_group.name,
        ahb_status="X [2499]",
        elements=(create_ahb_segment_from_mig(mig_segment_group.elements[0]),),
        # We only need to add the first segment here, because an application can detect the unused segment group here
        # and stop further traversal. The first segment is used for the segment number.
    )


def add_unused_data_elements_or_groups_to_ahb(
    mig_element: mig.Segment | mig.DataElementGroup, ahb_element: ahb.Segment | ahb.DataElementGroup
) -> None:
    """
    Adds unused MIG data elements to the AHB data element group.
    This ensures that all MIG elements are present in the AHB for parallel iteration.
    """
    edited_ahb_elements = list(ahb_element.data_elements)
    index = 0
    for cur_mig_element, cur_ahb_element in parallel_iter_segment_or_data_element_group(mig_element, ahb_element):
        if cur_ahb_element is None:
            # MIG element is unused in AHB, add it to AHB
            if isinstance(cur_mig_element, mig.DataElement):
                edited_ahb_elements.insert(index, create_ahb_data_element_from_mig(cur_mig_element))
            else:
                assert isinstance(cur_mig_element, mig.DataElementGroup)
                edited_ahb_elements.insert(index, create_ahb_data_element_group_from_mig(cur_mig_element))
        elif isinstance(cur_mig_element, mig.DataElementGroup):
            assert isinstance(cur_ahb_element, ahb.DataElementGroup)
            add_unused_data_elements_or_groups_to_ahb(cur_mig_element, cur_ahb_element)
        index += 1
    _set(ahb_element, "data_elements", tuple(edited_ahb_elements))
    assert len(ahb_element.data_elements) == len(mig_element.data_elements)


def add_unused_segment_or_groups_to_ahb(
    mig_root: mig.MessageImplementationGuide | mig.SegmentGroup, ahb_root: ahb.Anwendungsfall | ahb.SegmentGroup
) -> None:
    """ """
    edited_ahb_elements = list(ahb_root.elements)
    index = 0
    for mig_element, ahb_element in parallel_iter_segment_group_or_root(mig_root, ahb_root):
        if ahb_element is None:
            if isinstance(mig_element, mig.Segment):
                edited_ahb_elements.insert(index, create_ahb_segment_from_mig(mig_element))
            else:
                assert isinstance(mig_element, mig.SegmentGroup)
                edited_ahb_elements.insert(index, create_ahb_segment_group_from_mig(mig_element))
        else:
            if isinstance(mig_element, mig.Segment):
                assert isinstance(ahb_element, ahb.Segment)
                add_unused_data_elements_or_groups_to_ahb(mig_element, ahb_element)
            elif isinstance(mig_element, mig.SegmentGroup):
                assert isinstance(ahb_element, ahb.SegmentGroup)
                add_unused_segment_or_groups_to_ahb(mig_element, ahb_element)
        index += 1
    _set(ahb_root, "elements", tuple(edited_ahb_elements))
    assert len(ahb_root.elements) == len(mig_root.elements)


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


def sanitize_ahb(mig_root: mig.MessageImplementationGuide, ahb_root: ahb.Anwendungshandbuch) -> None:
    """
    Sanitizes the AHB by adding unused MIG data elements and groups to the AHB.
    """
    add_must_not_pattern_to_ahb_conditions(ahb_root)
    for anwendungsfall in ahb_root.anwendungsfaelle:
        add_unused_segment_or_groups_to_ahb(mig_root, anwendungsfall)
