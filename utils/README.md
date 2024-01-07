# Misc utils


# About

Useful bits of code to be used in various places in OpSim, importantly quick and simple time conversion.


## Misc Notes

```python
# Pretty print the dictionary we read from the input YAML, for an extra check:
def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))
```