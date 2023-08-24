# LuSEE-Night lander power

## About
Software for calculations related to power generation, management and storage

## Notes

The `docs` folder cotnains various helpful bits of documentation. In the `reference` forlder
there is a "sandbox" version of the original power calculation notebook (heavily modified and
not to be used for anything practical) and some requisite inputs. Kept for continuity with the
power calculation notebook. The folder `nav` contains utility accessor methods to interface
coordinate calculations.

## MJD

The MJD gives the number of days since midnight on November 17, 1858. This date corresponds to 2400000.5 days after
day 0 of the Julian calendar. MJD is still in common usage in tabulations by the U. S. Naval Observatory.
Care is needed in converting to other time units, however, as a result of the half day offset (unlike the Julian date,
the modified Julian date is referenced to midnight instead of noon) and because of the insertion of semiannual leap
seconds (which are inserted at midnight).

## Misc

On some Debian instances, the "backport" installation of the `lzma` Python package is needed for
some dependencies to work. This may be installed into a virtual environment, then referenced,
as shown in the following example:

```bash
export PYTHONPATH=/home/maxim/projects/lusee/luseepy:/home/maxim/.virtualenvs/lusee/lib/python3.10/site-packages/backports
```
