import great_expectations as gx
import pandas as pd
from pydantic import StrictStr
from pathlib import Path
import json
from typing import List


def add_not_null_expectations(expectations_suite: gx.ExpectationSuite, columns: List[str]):
    """
    Adds expectations to check that columns do not contain any null values.
    :param expectations_suite: ExpectationSuite object
    :param columns: list of columns that must not contain any null values
    :return: None
    """
    for col in columns:
        expectations_suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(
                column=col, severity="critical"
            )
        )


def add_sensor_msg_delta(df_: pd.DataFrame, ip: str, msgtype: float):
    mask = (df_["ip.src"] == ip) & (df_["mqtt.msgtype"] == msgtype)

    df_ = df_.sort_values("frame.time_epoch").copy()
    df_.loc[mask, "msg_delta"] = df_.loc[mask, "frame.time_epoch"].diff()

    return df_


# create data context
context = gx.get_context(mode="ephemeral")

# import data
df = pd.read_csv(Path('../../data/processed/training.csv'))

# add msg delta columns for both motion sensors
df = add_sensor_msg_delta(df, '192.168.0.154', 3.0) # (1)
df = add_sensor_msg_delta(df, '192.168.0.174', 3.0) # (2)

# connect to data
# create Data Source, Data Asset, Batch Definition, and Batch

data_source = context.data_sources.add_pandas("pandas")
data_asset = data_source.add_dataframe_asset(name="pd dataframe asset")

batch_definition = data_asset.add_batch_definition_whole_dataframe("batch definition")
batch = batch_definition.get_batch({StrictStr("dataframe"): df})

# --- create Expectation Suite ---
suite = context.suites.add(
    gx.core.expectation_suite.ExpectationSuite(name="expectations")
)
# strict no null tests
cols_cannot_be_null = ['frame.time_delta', 'frame.time_delta_displayed', 'frame.time_epoch',
       'frame.time_relative', 'frame.cap_len', 'frame.len', 'frame.number', 'ip.src']
add_not_null_expectations(suite, columns=cols_cannot_be_null)
# null test on mqtt.msgtype
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="mqtt.msgtype",
        mostly=0.60,
        severity="warning",
    )
)
# motion sensor (1)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column='msg_delta',
        min_value=0.99,
        max_value=1.06,
        row_condition="`ip.src` == '192.168.0.154' and `mqtt.msgtype` == 3.0",
        condition_parser="pandas",
        severity="warning"
    )
)
# motion sensor (2)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column='msg_delta',
        min_value=0.99,
        max_value=2.01,
        row_condition="`ip.src` == '192.168.0.174' and `mqtt.msgtype` == 3.0",
        condition_parser="pandas",
        severity="warning"
    )
)


# create Validation Definition
validation_definition = context.validation_definitions.add(
    gx.core.validation_definition.ValidationDefinition(
        name="validation definition",
        data=batch_definition,
        suite=suite,
    )
)

# create Checkpoint, run Checkpoint, and capture result
checkpoint = context.checkpoints.add(
    gx.checkpoint.checkpoint.Checkpoint(
        name="checkpoint", validation_definitions=[validation_definition]
    )
)

checkpoint_result = checkpoint.run(
    batch_parameters={"dataframe": df}
)

serializable_results = {}
for key, value in checkpoint_result.run_results.items():
    serializable_results[str(key)] = value.to_json_dict()

test_result_dir = Path('../../test_results')
test_result_dir.mkdir(exist_ok=True, parents=True)
with open(test_result_dir / "pre-training_validation_results.json", "w") as f:
    json.dump(serializable_results, f, indent=2)