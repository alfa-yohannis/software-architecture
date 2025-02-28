package mvi;

public class UpdateValueIntent implements Intent {

	String sourceName;
	String targetName;
	int value;

	public UpdateValueIntent(String sourceName, String targetName, int value) {
		this.sourceName = sourceName;
		this.targetName = targetName;
		this.value = value;
	}

	public String getSourceName() {
		return sourceName;
	}

	public void setSourceName(String sourceName) {
		this.sourceName = sourceName;
	}

	public String getTargetName() {
		return targetName;
	}

	public void setTargetName(String targetName) {
		this.targetName = targetName;
	}

	public int getValue() {
		return value;
	}

	public void setValue(int value) {
		this.value = value;
	}

}
