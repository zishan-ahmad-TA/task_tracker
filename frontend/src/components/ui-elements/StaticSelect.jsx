import Select from 'react-select';
import styles from './StaticSelect.module.css';

const StaticSelect = ({
    options,
    value,
    onChange,
    defaultValue = [],
    name,
    outlineColor = "#82C468",
    className = "basic-static-select",
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
        <div className={styles.StaticSelectContainer}>
            <Select
                defaultValue={defaultValue}
                value={value}
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

export default StaticSelect;
