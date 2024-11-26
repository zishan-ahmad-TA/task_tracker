import Select from 'react-select';
import styles from './MultiSelect.module.css';

const MultiSelect = ({
    options,
    value,
    onChange,
    defaultValue = [],
    name,
    outlineColor = "#82C468",
    className = "basic-multi-select",
    classNamePrefix = "select",
}) => {
    const customStyles = {
        control: (provided, state) => ({
            ...provided,
            borderColor: state.isFocused ? outlineColor : provided.borderColor,
            boxShadow: state.isFocused ? `0 0 0 1px ${outlineColor}` : 'none',
            '&:hover': {
                borderColor: state.isFocused ? outlineColor : provided.borderColor,
            },
        }),
    };

    return (
        <div className={styles.MultiSelectContainer}>
            <Select
                defaultValue={defaultValue}
                value={value}
                isMulti
                name={name}
                options={options}
                onChange={onChange}
                className={className}
                classNamePrefix={classNamePrefix}
                styles={customStyles}
            />
        </div>
    );
};

export default MultiSelect;
